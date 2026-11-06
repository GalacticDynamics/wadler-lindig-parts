"""Tests for the formatting engine itself -- the future `wadler-lindig-parts`.

Nothing here reaches for a quantity, a unit or an array library: these are the
tests that travel with `engine.py` and `generic.py` when they become their own
package, and they must pass with none of unxt's axes registered.
"""

import dataclasses
import pathlib
import re

import pytest
import wadler_lindig as wl

from wadler_lindig_parts import (
    ALIASES,
    AXES,
    Axis,
    doc_part,
    doc_to_str,
    engine as engine_module,
    examples,
    inert_axes,
    MARKUPS,
    parse_spec,
    parts_to_doc,
    parts_to_markup,
    PGroup,
    PPart,
    pparts,
    pspec,
    pvalue,
    register_alias,
    register_axis,
    register_markup,
    render,
    ReprMixin,
    REQUIRED_MARKUP_KEYS,
    Spec,
    unregister_alias,
    unregister_axis,
    unregister_markup,
    unwrap_math,
)
from wadler_lindig_parts.engine import _ALIASES, _AXES, _KEYWORDS, _MARKUPS
from wadler_lindig_parts.generic import _check_markup_row, _MARKUP_WORDS


# ============================================================================
# The grammar's own invariants


def test_keyword_namespace_is_pairwise_disjoint() -> None:
    """One word may never name two axes.

    This is the invariant that lets the keyword run be order-independent with
    no content-sniffing: if `_KEYWORDS` is a function of the word alone, then
    ``"html-bare"`` and ``"bare-html"`` cannot differ. A dict literal already
    enforces uniqueness of *keys*, so the real risk is a new word being added
    that collides with an `ALIASES` entry -- check that too.
    """
    assert not set(_KEYWORDS) & set(ALIASES)


def test_every_axis_applies_to_some_layout() -> None:
    """An axis no layout accepts would be unreachable."""
    for name, ax in AXES.items():
        assert ax.layouts, name


def test_every_keyword_maps_back_to_its_axis() -> None:
    """`_KEYWORDS` is the flat namespace `Axis.keywords` describes."""
    for name, ax in AXES.items():
        for word in ax.keywords:
            assert name in _KEYWORDS[word]


def test_spec_defaults_are_the_grammar_defaults() -> None:
    """An all-omitted spec is exactly ``Spec.of()``."""
    assert parse_spec("product") == Spec.of()


def test_keywords_are_order_independent() -> None:
    """A keyword run is a set, not a sequence."""
    assert parse_spec("html-bare") == parse_spec("bare-html")
    assert parse_spec("latex-type-mul") == parse_spec("mul-latex-type")


@pytest.mark.parametrize(
    ("spec", "value_spec"),
    [
        (".3g", ".3g"),  # bare: no keyword at all
        ("mul-.3g", ".3g"),  # after a keyword
        ("-.2f", "-.2f"),  # leading '-' is a sign flag, not a delimiter
        ("mul-->10.2f", "->10.2f"),  # embedded '-' is a fill character
        ("mul-.2f-.3g", ".2f-.3g"),  # everything after the first non-keyword
        ("mul", "values"),  # keywords only: the axis keeps its default
    ],
)
def test_scan_rule_splits_keywords_from_the_value_spec(
    spec: str, value_spec: str | None
) -> None:
    """The first non-keyword token ends keyword parsing; the rest is the spec.

    This one rule is what keeps the grammar unambiguous with an arbitrary
    Python format spec in play -- a format spec may contain ``-`` itself, and
    it can never be mistaken for a component boundary.
    """
    assert parse_spec(spec)["value"] == value_spec


@pytest.mark.parametrize("markup", sorted(MARKUPS))
def test_markup_row_defines_the_required_keys(markup: str) -> None:
    """These are the keys with no per-fragment fallback."""
    for key in REQUIRED_MARKUP_KEYS:
        assert key in MARKUPS[markup]


def test_plain_roles_are_escaped() -> None:
    """A downstream role carries a class name; ``<``/``&``/``_``/``%`` break output."""
    assert parts_to_markup((PPart("frame", "<A & B>"),), markup="html") == (
        "<span>&lt;A &amp; B&gt;</span>"
    )
    assert parts_to_markup((PPart("frame", "a_b 50%"),), markup="latex") == (
        r"$a\_b 50\%$"
    )


def _long_term_doc() -> wl.AbstractDoc:
    """A rendering long enough to break, owing nothing to units."""
    return parts_to_doc(pparts(examples.Term([float(i) for i in range(8)], "x")))


def test_layout_stays_inline_when_it_fits() -> None:
    assert "\n" not in doc_to_str(_long_term_doc(), 100)


def test_separator_ink_survives_a_break() -> None:
    """``BreakDoc`` shows its text only in horizontal mode.

    Mapping ``" * "`` straight to a ``BreakDoc`` silently dropped the ``*`` on
    the broken line.
    """
    out = doc_to_str(_long_term_doc(), 20)
    assert "\n" in out
    assert out.rstrip().endswith("x")
    assert "*" in out


def test_adjacent_separators_do_not_emit_a_blank_line() -> None:
    """A separator with no trailing space must not offer a break."""
    parts = (PPart("close", ")", "sep"), PPart("gap", " ", "sep"), PPart("frame", "@x"))
    assert not re.search(r"\n\s*\n", doc_to_str(parts_to_doc(parts), 3))


def _vector_parts(markup: str = "text") -> tuple:
    """A composite of two child renderings, owing nothing to units."""
    x = examples.Term([float(i) for i in range(6)], "x")
    y = examples.Term([float(i) for i in range(6)], "y")
    return (
        PPart("open", "(", "sep"),
        PGroup("child", pparts(x, markup=markup)),
        PPart("comma", ", ", "sep"),
        PGroup("child", pparts(y, markup=markup)),
        PPart("close", ")", "sep"),
        PPart("gap", " ", "sep"),
        PPart("frame", "@icrs"),
    )


def test_nesting_keeps_inner_groups_inline() -> None:
    """A wadler-lindig group is all-or-nothing.

    Splicing children flat means every break point breaks together, so the
    inner ``*`` separators break for no reason. This count is what fails if
    anyone re-flattens the tree.
    """
    out = doc_to_str(parts_to_doc(_vector_parts()), 46)
    assert "\n" in out  # the outer group did break
    assert out.count(" *\n") == 0  # ...but no inner one did


def test_nested_latex_has_exactly_one_dollar_pair() -> None:
    """Embedding rendered strings would give nested ``$...$`` and invalid LaTeX."""
    out = parts_to_markup(_vector_parts("latex"), markup="latex")
    assert out.startswith("$")
    assert out.endswith("$")
    assert "$" not in out[1:-1]


class _Uncertain:
    """A type introducing roles no markup has heard of."""

    def __init__(self, value: float, err: float, unit: str) -> None:
        self.value, self.err, self.unit = value, err, unit


@pparts.dispatch  # type: ignore[misc]
def _(obj: _Uncertain, /, *, markup: str = "text", **kw: object) -> tuple:
    return (
        PPart("value", f"{obj.value:g}"),
        PPart("pm", " ± ", "sep"),
        PPart("uncert", f"{obj.err:g}"),
        PPart("mul", " * ", "sep"),
        PPart("unit", obj.unit),
    )


def test_new_roles_work_with_no_markup_change() -> None:
    """``pm``/``uncert`` are unknown to text and html; each falls back to its text."""
    obj = _Uncertain(1.5, 0.2, "m")
    assert parts_to_markup(pparts(obj)) == "1.5 ± 0.2 * m"
    assert parts_to_markup(pparts(obj, markup="html"), markup="html") == (
        "<span>1.5</span> ± <span>0.2</span> * <span>m</span>"
    )


def test_a_markup_may_override_a_new_role() -> None:
    """LaTeX declares ``pm``; that is the whole cost of teaching it a role."""
    out = parts_to_markup(
        pparts(_Uncertain(1.5, 0.2, "m"), markup="latex"), markup="latex"
    )
    assert r"\pm" in out


def test_unregistered_type_degrades_rather_than_raising() -> None:
    """One unregistered field must not poison a whole object's repr."""
    assert (
        parts_to_markup(
            pparts(object.__new__(type("W", (), {"__str__": lambda _: "W!"})))
        )
        == "W!"
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (r"$\mathrm{m}$", r"\mathrm{m}"),  # wrapped: unwrapped once
        (r"\mathrm{m}", r"\mathrm{m}"),  # unwrapped: left intact
        ("$", "$"),  # lone delimiter: satisfies both ends
        ("", ""),
        ("$a", "$a"),
        ("a$", "a$"),
    ],
)
def test_unwrap_math_only_strips_real_delimiters(text: str, expected: str) -> None:
    r"""Slicing unconditionally corrupts an already-unwrapped fragment.

    ``\mathrm{m}`` would become ``mathrm{m`` -- the same defect fixed in
    ``_repr_latex_`` (#870), which this engine must not reintroduce.
    """
    assert unwrap_math(text) == expected


#: Every module in the package, discovered rather than listed. A hardcoded
#: tuple is a list that goes stale: `__init__.py` was added after this test was
#: written and was not in it, so the one module naming every public name was
#: the one module whose imports nobody checked.
_PACKAGE_DIR = pathlib.Path(engine_module.__file__).parent
_PACKAGE_MODULES = tuple(sorted(_PACKAGE_DIR.glob("*.py")))
#: Module stems a package-side module may reach with a single-dot relative
#: import. `__init__` is excluded: a submodule importing the package root
#: would be a cycle.
_PACKAGE_SIDE = tuple(sorted(p.stem for p in _PACKAGE_MODULES if p.stem != "__init__"))


def _import_offenders(source: str) -> list[str]:
    """Imports in `source` that a package-side module may not make.

    Allowed: `wadler_lindig`, `plum`, the standard library, and a
    single-dot relative import of another package-side module.
    """
    import ast  # noqa: PLC0415
    import sys  # noqa: PLC0415

    allowed = {"wadler_lindig", "plum", *sys.stdlib_module_names}
    bad = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            bad += [a.name for a in node.names if a.name.split(".")[0] not in allowed]
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if (node.module or "").split(".")[0] not in allowed:
                    bad.append(node.module or "")
            elif node.level != 1:
                bad.append("." * node.level + (node.module or ""))
            elif node.module is None:  # ``from . import x``
                bad += [f".{a.name}" for a in node.names if a.name not in _PACKAGE_SIDE]
            elif node.module not in _PACKAGE_SIDE:
                bad.append(f".{node.module}")
    return bad


def test_import_offenders_flags_what_it_should() -> None:
    """The boundary check is not vacuous."""
    assert _import_offenders("from .axes import foo") == [".axes"]
    assert _import_offenders("from .. import quantity") == [".."]
    assert _import_offenders("from . import axes") == [".axes"]
    assert _import_offenders("import numpy") == ["numpy"]
    assert _import_offenders("from jax import numpy") == ["jax"]
    assert not _import_offenders(
        "import os\nimport plum\nfrom .engine import x\nfrom . import generic\n"
        "from wadler_lindig import y"
    )


def test_the_example_type_renders_in_every_route() -> None:
    """The engine's own docs are written against this type.

    So it has to exercise the routes those docs demonstrate. Values here are
    measured, not assumed: `mul` leaves the object's own ``.`` separator
    alone, which is what the ``sep`` axis documents.
    """
    v = examples.Version(2, 1)
    assert repr(v) == "2.1"
    assert str(v) == "2.1"
    assert f"{v:bare}" == "2.1"
    assert f"{v:mul}" == "2.1"
    assert f"{v:html}" == "<span>2</span>.<span>1</span>"
    assert f"{v:latex}" == "$2.1$"


def test_the_engine_alone_registers_six_axes_and_no_aliases() -> None:
    """This package's registry holds its own six axes and nothing else.

    Zero aliases is the interesting number: the engine ships no shorthand at
    all. Every alias in existence is registered by a consumer, which is why
    this reads 0 here and 3 inside `unxt`.

    Read straight off the live registry. In-tree in `unxt` this had to copy
    the modules into a bare package and import them in a subprocess, because
    `unxt.__init__` registers its axes eagerly and the registry was already
    polluted by import time. There is no consumer here to hide from, so the
    subprocess was pure cost -- and a test that reads the thing it is asserting
    about cannot drift from it.
    """
    assert sorted(AXES) == ["indent", "layout", "markup", "sep", "value", "width"]
    assert len(ALIASES) == 0
    assert sorted(MARKUPS) == ["html", "latex", "text"]


def test_the_package_imports_only_wl_plum_and_stdlib() -> None:
    """Constitution principle I, as a command rather than a convention.

    Every module in the package may import `wadler_lindig`, `plum`, the
    standard library, and its siblings. Nothing else, ever -- a third runtime
    dependency cannot arrive without deleting this test, which a reviewer
    sees.

    The modules are globbed, not listed, so this covers a module added later.
    It is also the inverted form of the discipline: the test it replaced asked
    "does anything import `unxt`?", whose answer is permanently no and stays
    no while somebody adds `numpy`. This one asks "does anything import
    something it may not?", which is the question.
    """
    assert _PACKAGE_MODULES, "glob found no modules -- the test would be vacuous"
    for path in _PACKAGE_MODULES:
        offenders = _import_offenders(path.read_text(encoding="utf-8"))
        assert offenders == [], f"{path.name}: {offenders}"


def test_a_downstream_package_can_register_its_own_axis() -> None:
    """A downstream axis must be indistinguishable from a built-in one.

    This is the check the whole registry exists for: before it, `Spec` was a
    closed `NamedTuple` and this raised ``TypeError: Spec.__new__() got an
    unexpected keyword argument``. `coordinax` already carries exactly such an
    axis (``vector_form``) as an ad-hoc ``__pdoc__`` knob with no way to reach
    it from a format spec.

    The built-in keyword it is interleaved with is ``type``, from the ``value``
    axis -- one of the few that apply to the ``call`` layout. In-tree this used
    unxt's ``abbrev``, which does not exist here.
    """
    axis = Axis(
        name="demo_form",
        keywords={"demoform": True},
        default=False,
        layouts={"call": lambda v: {"demo_form": v}},
    )
    register_axis(axis)
    register_alias("demoalias", "call-demoform")
    try:
        assert parse_spec("call-demoform")["demo_form"] is True
        assert parse_spec("call")["demo_form"] is False  # default filled in
        assert parse_spec("demoalias") == parse_spec("call-demoform")
        # Order-independent alongside a built-in axis, like any other keyword.
        assert parse_spec("call-demoform-type") == parse_spec("type-demoform-call")
        # Scoped to its layouts, with the same typed error a built-in gets.
        with pytest.raises(ValueError, match="'demo_form' does not apply"):
            parse_spec("product-demoform")
    finally:
        unregister_axis("demo_form")
        unregister_alias("demoalias")


@pytest.mark.parametrize("word", ["html", "mul"])
def test_an_alias_never_collides_silently(word: str) -> None:
    """An alias has no qualified form, so a clash with one stays fatal.

    A keyword can be disambiguated as ``axis=word``; an alias is a whole spec
    and cannot, so both directions around an alias must still raise.

    The words are built-in keywords of this package (``html`` from ``markup``,
    ``mul`` from ``sep``). In-tree the second was unxt's ``compact`` alias,
    which does not exist here -- so the registration *succeeded*, the test
    failed with "DID NOT RAISE", and because it failed it never cleaned up.
    That left ``compact`` in `ALIASES` for the rest of the session, which is
    what made the next test below pass for entirely the wrong reason.
    """
    with pytest.raises(ValueError, match="already"):
        register_alias(word, "call-type")
    assert word not in ALIASES


def test_an_alias_name_may_not_be_claimed_as_a_keyword() -> None:
    """The other direction: a keyword may not take a name an alias holds.

    The alias has to be registered first. In-tree this leaned on unxt's
    ``compact`` already being one; here `ALIASES` starts empty, so a test
    asserting a clash has to create the thing it clashes with.
    """
    register_alias("tmp_alias_name", "call-type")
    try:
        with pytest.raises(ValueError, match="already an alias"):
            register_axis(
                Axis(
                    name="clash",
                    keywords={"tmp_alias_name": 1},
                    default=0,
                    layouts={"call": dict},
                )
            )
    finally:
        unregister_alias("tmp_alias_name")
    assert "clash" not in AXES


def test_only_one_axis_may_claim_free_text() -> None:
    """A spec has exactly one trailing run, so only one axis can receive it.

    Not a restriction so much as an observation about the scan rule: the run
    after the first non-keyword is terminal. Registering a second claimant is
    a mistake worth catching at registration rather than at parse.
    """
    with pytest.raises(ValueError, match="already does"):
        register_axis(
            Axis(
                name="second_free",
                keywords={"secondfree": 1},
                default=0,
                layouts={"product": dict},
                free_text=("product",),
            )
        )
    assert "second_free" not in AXES


def test_registering_an_axis_name_twice_is_an_error() -> None:
    """A second axis of the same name would shadow the first in `AXES`."""
    with pytest.raises(ValueError, match="already registered"):
        register_axis(
            Axis(name="value", keywords={"nope": 1}, default=0, layouts={"call": dict})
        )


def test_spec_of_rejects_an_unregistered_axis() -> None:
    """A typo'd axis would otherwise sit in the mapping and never be read."""
    with pytest.raises(ValueError, match="not registered axes"):
        Spec.of(markup="html", nonsuch="x")


def test_spec_repr_shows_every_axis() -> None:
    """`Spec` is a mapping, so it needs a repr of its own to be legible."""
    text = repr(Spec.of(layout="call"))
    assert text.startswith("Spec(")
    assert "layout='call'" in text


def test_a_probe_that_raises_is_skipped_not_propagated() -> None:
    """The inert check must never break the render it is only inspecting.

    A type may legitimately reject the *default* of an axis while accepting
    the value asked for. The probe swallows that and reports nothing for the
    axis, rather than turning a working format call into an exception.

    The axis is registered here rather than borrowed. In-tree this used
    unxt's ``unit_style`` axis and its ``name`` keyword; neither exists in
    this package, and a test for a *mechanism* should not need a consumer's
    vocabulary to express itself (principle II).
    """

    class Picky:
        pass

    @pparts.dispatch
    def _(obj: Picky, /, *, markup: str = "text", picky_style: str = "terse", **kw):
        if picky_style == "terse":  # the default -- what the probe re-renders with
            msg = "no terse form"
            raise RuntimeError(msg)
        return (PPart("label", picky_style),)

    register_axis(
        Axis(
            name="picky_style",
            keywords={"verbose": "verbose"},
            default="terse",
            layouts={"product": lambda v: {"picky_style": v}},
        )
    )
    try:
        obj = Picky()
        spec = parse_spec("verbose")
        assert pspec(obj, "verbose") == "verbose"
        assert inert_axes(obj, spec, render(obj, spec)) == []
    finally:
        unregister_axis("picky_style")


def test_a_render_error_without_free_text_keeps_its_own_exception() -> None:
    """Only a *value spec* failure is reworded as a bad format spec.

    A keyword-only spec that fails is the type's own error, and rewording it
    as "invalid format spec" would blame the spec for something it did not do.
    """

    class Exploding:
        pass

    @pparts.dispatch
    def _(obj: Exploding, /, *, markup: str = "text", **kw):
        msg = "boom from pparts"
        raise ValueError(msg)

    with pytest.raises(ValueError, match="boom from pparts"):
        pspec(Exploding(), "mul")


def test_sep_fragment_is_escaped_unless_overridden():
    """A downstream `sep` is escaped; a markup-table override is trusted."""
    parts = (PPart("a", "x"), PPart("lt", "<", "sep"), PPart("b", "y"))
    assert "&lt;" in parts_to_markup(parts, markup="html")
    assert r" \, " in parts_to_markup(
        (PPart("a", "x"), PPart("bare", " ", "sep"), PPart("b", "y")), markup="latex"
    )


@pytest.mark.parametrize("role", ["escape", "wrap", "vsep", "_content"])
def test_role_named_like_a_config_key_is_not_an_override(role):
    """`MARKUPS` rows mix config and per-role overrides in one namespace."""
    parts = (PPart(role, "x"), PPart(role, "-", "sep"), PPart(role, "y"))
    assert parts_to_markup(parts, markup="html") == "<span>x</span>-<span>y</span>"


def test_default_pvalue_needs_no_numpy():

    assert doc_to_str(pvalue("abc")) == "'abc'"
    assert doc_to_str(pvalue(3.14159, value_spec=".2f")) == "3.14"


def test_unregistered_type_degrades_to_str():
    """A type with no `pparts` renders as its `str`, so display never raises."""

    class Opaque:
        def __str__(self) -> str:
            return "opaque"

    assert pparts(Opaque()) == (PPart("value", "opaque"),)
    assert pspec(Opaque(), "html") == "<span>opaque</span>"


def test_unregistered_type_rejects_a_value_spec():
    """No value a spec could format: say so, not a different rendering."""
    with pytest.raises(TypeError, match="does not support a value format spec"):
        pspec(object(), ".2f")


def test_a_repr_routed_through_the_engine_without_pparts_does_not_recurse() -> None:
    """The str fallback must refuse re-entry rather than loop.

    A hand-written ``__repr__`` calling `pspec` has no `ReprMixin` dispatch to
    catch a missing `pparts`, so the fallback would render it with ``str`` and
    ``str`` would come straight back. The error names the omission instead.
    """

    @dataclasses.dataclass
    class Loop:
        x: int

        def __repr__(self) -> str:
            return pspec(self, "bare")

    with pytest.raises(TypeError, match="would recurse"):
        repr(Loop(1))


def test_the_recursion_guard_releases_its_object() -> None:
    """A tripped guard must not poison later renders of the same object.

    The guard keys on ``id``, so a leaked key would make the second render of
    an object fail, and a nested render of a *different* unregistered value
    fail with it.
    """
    obj = object()
    assert pspec(obj, "bare") == str(obj)
    assert pspec(obj, "bare") == str(obj)

    class Nests:
        def __str__(self) -> str:
            inner = pspec(object(), "bare")[:6]
            return f"nests({inner})"

    assert pspec(Nests(), "bare") == "nests(<objec)"


def test_ppart_doc_defaults_to_none_and_keeps_text():
    assert PPart("value", "1.0").doc is None


def test_doc_part_keeps_flat_text_and_the_doc():
    doc = wl.bracketed(
        begin=wl.TextDoc("["),
        docs=[wl.TextDoc("1."), wl.TextDoc("2.")],
        sep=wl.comma,
        end=wl.TextDoc("]"),
        indent=1,
    )
    part = doc_part("value", doc)
    assert part.text == "[1., 2.]"
    assert part.doc is doc


def test_text_layout_uses_the_part_doc_so_width_reaches_it():
    doc = wl.bracketed(
        begin=wl.TextDoc("["),
        docs=[wl.TextDoc(str(i)) for i in range(8)],
        sep=wl.comma,
        end=wl.TextDoc("]"),
        indent=1,
    )
    parts = (doc_part("value", doc), PPart("mul", " * ", "sep"), PPart("unit", "m"))
    assert doc_to_str(parts_to_doc(parts), 88) == "[0, 1, 2, 3, 4, 5, 6, 7] * m"
    narrow = doc_to_str(parts_to_doc(parts), 10)
    assert "\n" in narrow
    assert max(map(len, narrow.splitlines())) <= 10


def test_registries_are_read_only_views():
    for reg in (AXES, ALIASES, MARKUPS):
        with pytest.raises(TypeError):
            reg["x"] = 1  # type: ignore[index]


def test_register_axis_rejects_a_duplicate_unless_replace():
    ax = Axis("tmp_axis", {"tmpword": 1}, 0, {"call": lambda _: {}})
    register_axis(ax)
    try:
        with pytest.raises(ValueError, match="already registered"):
            register_axis(ax)
        register_axis(ax, replace=True)
        assert "tmp_axis" in AXES
    finally:
        unregister_axis("tmp_axis")
    assert "tmp_axis" not in AXES
    assert "tmpword" not in _KEYWORDS


def test_register_alias_replace():
    register_alias("tmp_alias", "bare")
    try:
        with pytest.raises(ValueError, match="already registered"):
            register_alias("tmp_alias", "mul")
        register_alias("tmp_alias", "mul", replace=True)
        assert ALIASES["tmp_alias"] == "mul"
    finally:
        unregister_alias("tmp_alias")
    assert "tmp_alias" not in ALIASES


_GOOD_ROW = {"_content": "[{}]", "wrap": "{}", "vsep": ", ", "escape": None}


@pytest.mark.parametrize(
    ("bad", "match"),
    [
        ({"wrap": "no braces"}, "wrap"),
        ({"wrap": "{}{}"}, "wrap"),
        ({"wrap": 3}, "wrap"),
        ({"_content": "{}{}"}, "_content"),
        ({"_content": "{x}"}, "_content"),
        ({"_content": "{"}, "_content"),
        ({"_content": None}, "_content"),
    ],
)
def test_register_markup_rejects_a_malformed_template(bad, match):
    with pytest.raises(ValueError, match=match):
        register_markup("bad_markup", {**_GOOD_ROW, **bad})
    assert "bad_markup" not in MARKUPS
    assert "bad_markup" not in _KEYWORDS


@pytest.mark.parametrize("content", ["", "<{0}>", "{}", "plain"])
def test_register_markup_accepts_any_content_str_that_formats(content):
    register_markup("ok_markup", {**_GOOD_ROW, "_content": content})
    unregister_markup("ok_markup")


@pytest.mark.parametrize("markup", sorted(MARKUPS))
def test_builtin_markup_rows_satisfy_the_register_markup_checks(markup):
    _check_markup_row(MARKUPS[markup])


def _snapshot():
    return (
        dict(_AXES),
        {k: list(v) for k, v in _KEYWORDS.items()},
        dict(_ALIASES),
        {k: dict(v) for k, v in _MARKUPS.items()},
        dict(_MARKUP_WORDS),
    )


def test_a_failed_replace_leaves_every_registry_untouched():
    before = _snapshot()
    with pytest.raises(ValueError, match="claims free text"):
        register_axis(AXES["sep"]._replace(free_text=("product",)), replace=True)
    assert _snapshot() == before
    assert parse_spec("bare")["sep"] == "bare"


def test_a_keyword_clash_on_replace_leaves_the_old_axis():
    """A rejected replacement must not take the axis it meant to replace.

    The alias is registered here. In-tree this clashed against unxt's
    ``compact``; with no alias of that name in this package the replacement
    *succeeded*, swapping the real ``sep`` axis for one whose only keyword was
    ``compact`` -- and since the test failed on DID NOT RAISE, it never
    restored it. Three later tests then failed on a ``sep`` axis that had lost
    ``mul`` and ``bare``, two of them only in a full run.
    """
    register_alias("tmp_clash_alias", "call-type")
    before = _snapshot()
    clash = AXES["sep"]._replace(keywords={"tmp_clash_alias": 1})
    try:
        with pytest.raises(ValueError, match="already an alias"):
            register_axis(clash, replace=True)
        assert _snapshot() == before
    finally:
        unregister_alias("tmp_clash_alias")
    assert parse_spec("mul")["sep"] == "mul"


def test_a_successful_replace_keeps_keywords_consistent():
    old = AXES["sep"]
    new = old._replace(keywords={"mul": "mul", "bare": "bare", "tmpsep": "mul"})
    register_axis(new, replace=True)
    try:
        assert _KEYWORDS["tmpsep"] == ["sep"]
        assert _KEYWORDS["mul"].count("sep") == 1
    finally:
        register_axis(old, replace=True)
    assert "tmpsep" not in _KEYWORDS
    assert _KEYWORDS["bare"].count("sep") == 1


def test_register_markup_rejects_a_keyword_clash():
    with pytest.raises(ValueError, match="keyword or alias"):
        register_markup("mul", _GOOD_ROW)
    assert "mul" not in MARKUPS


def test_width_does_not_eat_a_format_spec() -> None:
    assert parse_spec("mul-width=40-.2f")["value"] == ".2f"
    assert parse_spec(">10.2f")["value"] == ">10.2f"


def test_width_and_indent_are_not_bare_words() -> None:
    spec = parse_spec("mul")
    assert spec["width"] is None
    assert spec["indent"] is None
    assert "width" not in _KEYWORDS
    assert "40" not in _KEYWORDS
    assert parse_spec("width=40")["width"] == 40


def test_count_mapping_claims_no_bare_word():
    """`width`/`indent` take digits only through `axis=<n>`, never as a bare word."""
    from wadler_lindig_parts.engine import _Count  # noqa: PLC0415

    count = _Count()
    assert (len(count), list(count), count["12"]) == (0, [], 12)
    with pytest.raises(KeyError):
        count["m"]


@pytest.mark.parametrize("markup", ["text", "html", "latex"])
def test_width_reaches_every_markup(markup):
    """A narrow width breaks in every markup; wrappers no longer inflate it.

    Built from fragments rather than a `Quantity` on purpose: this is a claim
    about the layout, and routing it through a real value would make it depend
    on whether that value rendered in full -- a traced array comes out as a
    shape summary, which has nothing to wrap.
    """
    parts = (
        PPart("value", "x" * 30),
        PPart("mul", " * ", "sep"),
        PPart("unit", "m"),
    )
    doc = parts_to_doc(parts, markup=markup)
    assert "\n" in doc_to_str(doc, 20)
    # The flat path is what `_repr_html_` / `_repr_latex_` use, and it is still
    # one line -- markup gained layout without its string changing.
    assert "\n" not in doc_to_str(doc, 10**9)
    assert "\n" not in parts_to_markup(parts, markup=markup)


def test_register_markup_rejects_a_non_callable_escape():
    with pytest.raises(ValueError, match="escape"):
        register_markup("bad_escape", {**_GOOD_ROW, "escape": "x"})
    assert "bad_escape" not in MARKUPS


@pytest.mark.parametrize("content", ["{0.foo}", "{0[a]}"])
def test_register_markup_rejects_attribute_or_index_content(content):
    with pytest.raises(ValueError, match="_content"):
        register_markup("bad_content", {**_GOOD_ROW, "_content": content})
    assert "bad_content" not in MARKUPS


@pytest.mark.parametrize("short_arrays", [False, True])
def test_default_pvalue_non_compact_goes_through_wl_pdoc(short_arrays):
    """The numpy-free default also serves the ``array``/``type`` forms."""
    assert doc_to_str(pvalue("a<b", short_arrays=short_arrays)) == "'a<b'"
    assert (
        doc_to_str(pvalue("a<b", short_arrays=short_arrays, markup="html"))
        == "&#x27;a&lt;b&#x27;"
    )


# ============================================================================
# The contracts that crossed the distribution boundary
#
# Three behaviours that were implementation detail while these modules lived
# inside `unxt`, and are contract now that the registrants are separate
# distributions. Each was written and watched failing before being relied on
# (constitution principle V); the edit that makes each one fail is named in
# its docstring.


def _tmp_axis(name: str, word: str) -> Axis:
    """An axis claiming one keyword, for collision tests."""
    return Axis(
        name=name,
        keywords={word: f"{name}:{word}"},
        default=None,
        layouts={"product": lambda v: {name: v}},
    )


def test_two_axes_may_claim_one_keyword_and_the_bare_word_then_raises() -> None:
    """Constitution principle IV, as the code actually implements it.

    Keywords live in one flat namespace shared by every registering
    distribution, so two libraries may want one word. Both registrations
    *succeed* -- `_KEYWORDS` holds a list of claimants, not a winner. The
    refusal lands when a spec uses the word bare, and names both claimants
    and both qualified forms.

    `register_axis` deliberately does not refuse the second claim. Refusing it
    would leave nothing for ``axis=word`` to resolve to, which is principle
    IV's third bullet and the one substantive commitment of the three: a
    shared word is an inconvenience, not a defeat.

    Watched failing by changing `register_axis`'s
    ``_KEYWORDS.setdefault(word, []).append(axis.name)`` to
    ``_KEYWORDS[word] = [axis.name]`` -- first-claimant-loses rather than
    both-recorded. The bare word then resolves silently to the second axis and
    this test fails on the `pytest.raises`.
    """
    register_axis(_tmp_axis("first_claimant", "shared"))
    register_axis(_tmp_axis("second_claimant", "shared"))
    try:
        # Both registrations stood. Neither "won".
        assert sorted(_KEYWORDS["shared"]) == ["first_claimant", "second_claimant"]

        # The bare word is refused, naming both claimants and both escapes.
        with pytest.raises(ValueError, match="ambiguous keyword") as excinfo:
            parse_spec("shared")
        msg = str(excinfo.value)
        assert "'first_claimant'" in msg
        assert "'second_claimant'" in msg
        assert "first_claimant=shared" in msg
        assert "second_claimant=shared" in msg

        # And each qualified form still resolves, to its own axis.
        assert parse_spec("first_claimant=shared")["first_claimant"] == (
            "first_claimant:shared"
        )
        assert parse_spec("second_claimant=shared")["second_claimant"] == (
            "second_claimant:shared"
        )
    finally:
        unregister_axis("second_claimant")
        unregister_axis("first_claimant")
    assert "shared" not in _KEYWORDS


@pytest.mark.parametrize("missing", REQUIRED_MARKUP_KEYS)
def test_a_markup_row_missing_a_required_key_is_refused_at_registration(
    missing: str,
) -> None:
    """A row the renderers could not use is refused when it is registered.

    "At registration, not at render" is the substance: a row that passed
    registration and failed at render would fail in whichever consumer
    happened to format an object first, at a call site with nothing to do with
    the registration -- which may be in another distribution entirely. So the
    second half of this test, that no registry holds a partial entry, is the
    half that carries the claim.

    The existing `test_register_markup_rejects_a_malformed_template`
    parametrises six bad rows; every one supplies all four keys and corrupts a
    *value*, so the missing-key branch was unexercised.

    Watched failing by commenting out the ``if missing := ...`` block at the
    top of `generic._check_markup_row`: registration then succeeds for a row
    with no ``vsep``, and the `KeyError` surfaces at render instead.
    """
    row = {k: v for k, v in _GOOD_ROW.items() if k != missing}
    with pytest.raises(ValueError, match="missing required keys") as excinfo:
        register_markup("incomplete_markup", row)
    assert missing in str(excinfo.value)
    # Nothing partial left behind, in either registry it would touch.
    assert "incomplete_markup" not in MARKUPS
    assert "incomplete_markup" not in _KEYWORDS
    assert "incomplete_markup" not in _MARKUP_WORDS


def test_a_repr_spec_naming_an_unregistered_axis_fails_at_class_creation() -> None:
    """`ReprMixin` resolves ``__repr_spec__`` when the class is created.

    So a consumer must register its axes *before* defining the classes whose
    repr specs name them. Inside one package that was a statement about the
    order of lines in an ``__init__``; between two installed distributions it
    is load order between them, and the error arrives at a ``class`` statement
    that looks unrelated to the registration. That is why the README says so
    explicitly rather than leaving it to the message.

    `test_bad_repr_spec_fails_at_class_creation` in ``test_downstream.py``
    covers a spec that is invalid in any registry. This covers the
    registration-*order* case: the same spec, valid once the axis exists.

    Watched failing by moving the `parse_spec` call out of
    `ReprMixin.__init_subclass__` into `__repr__`: the class then defines
    cleanly and the error moves to first print.
    """
    spec = "lateform"

    # Before registration: the class statement itself is the failure.
    with pytest.raises(ValueError, match="invalid format spec"):

        class TooEarly(ReprMixin):
            __repr_spec__ = spec

    register_axis(_tmp_axis("late_axis", spec))
    try:
        # After registration: the identical spec is accepted, at class
        # creation, and resolved once rather than on every print.
        class LateEnough(ReprMixin):
            __repr_spec__ = spec

        assert LateEnough._repr_spec_parsed["late_axis"] == f"late_axis:{spec}"
    finally:
        unregister_axis("late_axis")


def test_a_name_containing_the_separator_is_refused_at_registration() -> None:
    """`-` joins components, so no registered name may contain one.

    `parse_spec` splits on ``-`` before it looks anything up, so a name with a
    ``-`` in it can never be the thing that is looked up. Registration used to
    accept such a name and the word was then simply unusable: `register_axis`
    returned normally, the keyword never resolved, and -- the part that makes
    this worth refusing rather than documenting -- ``axis=word`` did not
    rescue it either, because the qualified form is split on ``-`` first too.
    The alias case was worse still: `parse_spec` returned a `Spec` full of
    *defaults* rather than raising, so the mistake surfaced later, as a
    complaint about an invalid Python format spec.

    All three entry points that write into `_KEYWORDS` are covered, because
    all three have the same defect: an axis's name and its keywords, an alias
    name, and a markup name.

    Watched failing before the guard existed: every one of these registrations
    was accepted, so each `pytest.raises` failed on DID NOT RAISE.
    """
    bad = "two-words"

    # An axis's keyword.
    with pytest.raises(ValueError, match="may not contain"):
        register_axis(_tmp_axis("hyphen_keyword", bad))
    assert "hyphen_keyword" not in AXES

    # An axis's own name, which is what `axis=word` is spelled with.
    with pytest.raises(ValueError, match="may not contain"):
        register_axis(_tmp_axis(bad, "fine"))
    assert bad not in AXES
    assert "fine" not in _KEYWORDS

    # An alias name. Its *expansion* is a whole spec and so is full of
    # separators -- that is the point of an alias -- but its name is a token.
    with pytest.raises(ValueError, match="may not contain"):
        register_alias(bad, "html-mul")
    assert bad not in ALIASES

    # A markup name, which `register_markup` also publishes as a keyword.
    with pytest.raises(ValueError, match="may not contain"):
        register_markup(bad, MARKUPS["text"])
    assert bad not in MARKUPS
    assert bad not in _KEYWORDS


# ============================================================================
# Registration identity
#
# These two guard a failure that is silent, which is the only reason they are
# worth their lines. It happened once, in `unxt`, before the extraction: a
# doctest runner imported the engine through a second module path, so the
# `@pparts.dispatch` calls in `examples` registered onto a `plum.Function` that
# nothing ever called. `Term` then resolved to a generic method and rendered as
# *one* fragment -- the whole of `[1.0, 2.0] * x` as a single `PPart` -- instead
# of coefficient, operator and symbol. Every route still returned a string, so
# it read as a layout quirk rather than a dispatch failure, and the only tell
# was a separator that ignored its markup: `$[1.0, 2.0] * x$` where LaTeX owed
# `\,`.


def test_registration_lands_on_the_function_that_is_called() -> None:
    """One `pparts` across the package, the engine module and `examples`.

    Identity is what to assert, because the symptom is not an exception: a
    split registry renders, it just renders the wrong decomposition.
    """
    assert pparts is engine_module.pparts
    assert examples.pparts_term is pparts
    assert examples.pparts_version is pparts

    # And the registration a split would orphan actually answers.
    assert len(pparts(examples.Term([1.0, 2.0], "x"))) == 3


def test_an_unregistered_reprmixin_subclass_cannot_fail_silently() -> None:
    """A `ReprMixin` subclass with no `pparts` raises rather than degrading.

    This is what keeps the failure above loud here. A generic method that fell
    back to `str(obj)` in one fragment would make a missing registration render
    plausibly, which is exactly how the `unxt` case survived a test run.
    """

    @dataclasses.dataclass(repr=False)
    class Unregistered(ReprMixin):
        value: object

        __repr_spec__ = "mul"

    with pytest.raises(TypeError, match="registers no pparts"):
        pparts(Unregistered(1.0))
