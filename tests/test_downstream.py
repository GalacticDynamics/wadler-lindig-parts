"""A type outside unxt, using only the public `pparts` surface (no numpy)."""

import dataclasses
import pathlib
import subprocess
import sys
import textwrap
from typing import Any

import pytest
import wadler_lindig as wl

from wadler_lindig_parts import (
    parse_spec,
    PPart,
    pparts,
    pspec,
    register_alias,
    render,
    render_options,
    ReprMixin,
    Spec,
    unregister_alias,
)
from wadler_lindig_parts.examples import Point, Version


def test_every_route_comes_from_one_pparts():
    v = Version(1, 2)
    assert repr(v) == "1.2"
    assert str(v) == "1.2"
    assert f"{v}" == "1.2"
    assert f"{v:html}" == "<span>1</span>.<span>2</span>"
    assert f"{v:latex}" == "$1.2$"
    assert v._repr_html_() == "<span>1</span>.<span>2</span>"
    assert v._repr_latex_() == "$1.2$"
    assert wl.pformat(v) == "1.2"
    assert pspec(v, "") == str(v)


def test_bad_repr_spec_fails_at_class_creation():
    with pytest.raises(ValueError, match="invalid format spec"):

        class Bad(ReprMixin):
            __repr_spec__ = "nonsense-axis"


@pytest.mark.parametrize(
    "spec", ["bare", "mul", "html", ".2f", "mul-.2f", "call", "d", "x", "s"]
)
def test_good_repr_specs_are_accepted(spec):
    class Ok(ReprMixin):
        __repr_spec__ = spec

    assert Ok._repr_spec_parsed is not None


def test_an_alias_must_exist_before_the_class():
    with pytest.raises(ValueError, match="invalid format spec"):

        class Early(ReprMixin):
            __repr_spec__ = "later_alias"

    register_alias("later_alias", "bare")  # registered after: too late for Early
    try:

        class Late(ReprMixin):
            __repr_spec__ = "later_alias"

        assert Late._repr_spec_parsed["sep"] == "bare"
    finally:
        unregister_alias("later_alias")


def test_spec_is_inherited_and_overridable():
    class Mid(ReprMixin):
        __repr_spec__ = "mul"

    class Leaf(Mid):
        pass

    class Over(Mid):
        __repr_spec__ = "bare"

    assert Leaf._repr_spec_parsed["sep"] == "mul"
    assert Over._repr_spec_parsed["sep"] == "bare"


def test_dataclass_repr_true_would_shadow_the_mixin():
    """Documented hazard: @dataclass (repr=True) wins over an inherited __repr__."""

    @dataclasses.dataclass
    class Shadowed(ReprMixin):
        x: int

    assert "Shadowed(x=1)" in repr(Shadowed(1))  # dataclass repr, not the mixin's


def test_pformat_matches_repr_for_product_spec():
    @dataclasses.dataclass(repr=False)
    class Pt(ReprMixin):
        x: int

    @pparts.dispatch
    def _(obj: Pt, /, *, markup="text", **kw):
        return (PPart("x", str(obj.x)), PPart("u", "m", "unit"))

    assert wl.pformat(Pt(3)) == repr(Pt(3))


@pytest.mark.parametrize("spec", ["product", "call"])
def test_missing_pparts_raises_on_every_route_that_needs_it(spec):
    @dataclasses.dataclass(repr=False)
    class N(ReprMixin):
        """Forgot to register pparts."""

        x: int
        __repr_spec__ = spec

    msg = "N subclasses ReprMixin but registers no pparts"
    # A ``call`` dataclass renders its fields without any fragments, so only
    # the fragment routes need the missing registration.
    calls = [lambda o: f"{o:mul}"]
    if spec == "call":
        for call in (repr, str, wl.pformat):
            assert call(N(1)).endswith(".N(x=1)")
    else:
        calls += [repr, str, wl.pformat]
    for call in calls:
        with pytest.raises(TypeError, match=msg):
            call(N(1))


def test_pdoc_applies_the_class_spec():
    @dataclasses.dataclass(repr=False)
    class B(ReprMixin):
        """Bare layout with a mul separator part."""

        x: int
        __repr_spec__ = "bare"

    @pparts.dispatch
    def _(obj: B, /, *, markup="text", **kw):
        return (
            PPart("value", str(obj.x)),
            PPart("mul", " * ", "sep"),
            PPart("unit", "m"),
        )

    assert repr(B(3)) == "3 m"
    assert wl.pformat(B(3)) == "3 m"
    assert wl.pformat([B(3)]) == repr([B(3)]) == "[3 m]"


def test_engine_and_generic_import_without_numpy_or_jax():
    """The package side needs only `wadler_lindig` and `plum`.

    The two modules are loaded as a synthetic package (bypassing ``unxt``'s
    own ``__init__``, which imports numpy/jax) with those libraries blocked.
    """
    import wadler_lindig_parts as fmt  # noqa: PLC0415

    code = textwrap.dedent(
        f"""
        import dataclasses, importlib, sys, types
        for name in ("numpy", "jax", "astropy", "quax"):
            sys.modules[name] = None
        pkg = types.ModuleType("fmtpkg")
        pkg.__path__ = [{str(pathlib.Path(fmt.__file__).parent)!r}]
        sys.modules["fmtpkg"] = pkg
        engine = importlib.import_module("fmtpkg.engine")
        importlib.import_module("fmtpkg.generic")
        import wadler_lindig as wl

        @dataclasses.dataclass(repr=False)
        class V(engine.ReprMixin):
            a: int
            b: int
            __repr_spec__ = "bare"

        @engine.pparts.dispatch
        def _(obj: V, /, *, markup="text", **kw):
            return (
                engine.PPart("a", str(obj.a)),
                engine.PPart("dot", ".", "sep"),
                engine.PPart("b", str(obj.b)),
            )

        v = V(1, 2)
        assert repr(v) == "1.2", repr(v)
        assert format(v, "html") == "<span>1</span>.<span>2</span>"
        assert wl.pformat(v) == "1.2"
        assert "numpy" not in sys.modules or sys.modules["numpy"] is None
        """
    )
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_call_dataclass_can_build_fragments_from_its_own_pdoc():
    """A ``call`` dataclass's fragments may reuse wadler-lindig's field layout.

    Before the mixin stepped aside under ``call``, `wl.pdoc` here reached the
    mixin's ``__pdoc__``, which asked `pparts` again, without end.
    """

    @dataclasses.dataclass(repr=False)
    class Box(ReprMixin):
        __repr_spec__ = "call"
        a: int
        b: str

    @pparts.dispatch
    def _(obj: Box, /, *, markup="text", **kw):
        return (PPart("value", wl.pformat(obj, width=10**9)),)

    box = Box(1, "<x>")
    assert repr(box).endswith(".Box(a=1, b='<x>')")
    assert f"{box:html}".endswith(".Box(a=1, b=&#x27;&lt;x&gt;&#x27;)</span>")


def test_repr_html_and_latex_are_flat():
    """HTML collapses whitespace and LaTeX math ignores newlines: no breaks."""

    @dataclasses.dataclass(repr=False)
    class Long(ReprMixin):
        n: int

    @pparts.dispatch
    def _(obj: Long, /, *, markup="text", **kw):
        parts = []
        for i in range(obj.n):
            parts += [PPart(f"p{i}", "word" * 5), PPart("mul", " * ", "sep")]
        return tuple(parts[:-1])

    long = Long(10)
    assert "\n" in repr(long)
    html, latex = long._repr_html_(), long._repr_latex_()
    assert html is not None
    assert latex is not None
    assert "\n" not in html
    assert "\n" not in latex


@pytest.mark.parametrize("registered", [True, False])
def test_call_types_show_their_repr_in_a_notebook(registered):
    """A constructor expression has no markup form, so the hooks step aside.

    Without this a ``call`` dataclass with no `pparts` raised in both hooks,
    and one with `pparts` showed fragments in a notebook but a constructor in
    a terminal.
    """

    @dataclasses.dataclass(repr=False)
    class Pair(ReprMixin):
        __repr_spec__ = "call"
        a: int

    if registered:

        @pparts.dispatch
        def _(obj: Pair, /, *, markup="text", **kw):
            return (PPart("a", str(obj.a)),)

    assert Pair(1)._repr_html_() is None
    assert Pair(1)._repr_latex_() is None


def test_notebook_hooks_follow_the_class_spec():
    """A ``mul`` type keeps its operator in a notebook, as ``repr`` does."""
    from wadler_lindig_parts.examples import Term

    t = Term([1.0, 2.0], "x")
    assert repr(t) == "[1.0, 2.0] * x"
    assert t._repr_html_() == "<span>[1.0, 2.0]</span> * <span>x</span>"


def test_call_type_without_a_constructor_keeps_its_markup():
    """No dataclass and no ``__pdoc__``: ``repr`` is fragments, so is the HTML."""

    class Bare(ReprMixin):
        __repr_spec__ = "call"

        def __init__(self, a):
            self.a = a

    @pparts.dispatch
    def _(obj: Bare, /, *, markup="text", **kw):
        return (PPart("a", str(obj.a)),)

    assert repr(Bare(1)) == "1"
    assert Bare(1)._repr_html_() == "<span>1</span>"


def test_call_type_with_its_own_pdoc_shows_its_repr_in_a_notebook():
    class Own(ReprMixin):
        __repr_spec__ = "call"

        def __init__(self, a):
            self.a = a

        def __pdoc__(self, **kw):
            return wl.TextDoc(f"Own({self.a})")

    assert repr(Own(1)) == "Own(1)"
    assert Own(1)._repr_html_() is None


class _Payload:
    """Stands in for an array: wadler-lindig would print it in full."""

    def __repr__(self) -> str:
        return "Payload([1, 2, 3])"


def _short_payload(obj):
    return wl.TextDoc("payload[3]") if isinstance(obj, _Payload) else None


def _short_under_type(spec):
    return {"custom": _short_payload} if spec["value"] == "type" else {}


def _holder(spec_string, options=_short_under_type):
    @dataclasses.dataclass(repr=False)
    class Holder(ReprMixin):
        __repr_spec__ = spec_string
        a: Any

    @render_options.dispatch
    def _(obj: Holder, /, *, spec):
        return options(spec)

    return Holder


def test_render_options_reach_call_routes_and_can_depend_on_the_spec():
    h = _holder("call-type-width=200")(_Payload())
    assert repr(h).endswith(".Holder(a=payload[3])")
    assert str(h) == repr(h)
    assert f"{h:call-type-width=200}" == repr(h)
    assert f"{h:call-array-width=200}".endswith(".Holder(a=Payload([1, 2, 3]))")


def test_render_options_stay_out_of_product_layout():
    """They are `wl.pformat` options, so a fragment route never sees them."""
    holder = _holder("call")
    seen = {}

    @pparts.dispatch
    def _(obj: holder, /, *, markup="text", **kw):
        seen.update(kw)
        return (PPart("value", "v"),)

    assert pspec(holder(_Payload()), "type") == "v"
    assert "custom" not in seen


def test_extra_overrides_render_options():
    holder = _holder("call", lambda _: {"custom": _short_payload})
    h = holder(_Payload())
    spec = parse_spec("call-width=200")
    assert render(h, spec).endswith(".Holder(a=payload[3])")
    out = render(h, spec, custom=lambda _: None)
    assert out.endswith(".Holder(a=Payload([1, 2, 3]))")


@pytest.mark.parametrize("key", ["width", "indent", "short_arrays"])
def test_render_options_may_not_set_what_the_spec_controls(key):
    """A type's option must not silently beat the caller's spec."""
    h = _holder("call", lambda _: {key: 1})(_Payload())
    with pytest.raises(
        ValueError, match=f"sets \\['{key}'\\], which the spec controls"
    ):
        repr(h)


def test_render_options_must_return_a_mapping():
    h = _holder("call", lambda _: None)(_Payload())
    with pytest.raises(TypeError, match="returned NoneType, not a mapping"):
        repr(h)


def test_base_and_subclass_may_annotate_spec_differently():
    """``spec`` is keyword-only, so plum dispatches on ``obj`` alone."""

    @dataclasses.dataclass(repr=False)
    class Base(ReprMixin):
        __repr_spec__ = "call-width=200"
        a: Any

    @dataclasses.dataclass(repr=False)
    class Sub(Base):
        pass

    @render_options.dispatch
    def _(obj: Base, /, *, spec: Spec):
        return {}

    @render_options.dispatch
    def _(obj: Sub, /, *, spec):
        return {"custom": _short_payload}

    assert repr(Base(_Payload())).endswith(".Base(a=Payload([1, 2, 3]))")
    assert repr(Sub(_Payload())).endswith(".Sub(a=payload[3])")


def test_an_outer_pformat_uses_its_own_options():
    """Documented limit: a ``__pdoc__`` cannot change its caller's options."""
    h = _holder("call-type-width=200")(_Payload())
    assert wl.pformat(h, width=200).endswith(".Holder(a=Payload([1, 2, 3]))")


def test_types_without_render_options_get_none():
    assert dict(render_options(Point(1.0, 2.0), spec=parse_spec("call"))) == {}
    assert pspec(Point(1.0, 2.0), "call") == "Point(x=1.0, y=2.0)"
