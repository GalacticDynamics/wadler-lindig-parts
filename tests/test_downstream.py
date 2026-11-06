"""A type outside unxt, using only the public `pparts` surface (no numpy)."""

import dataclasses
import pathlib
import subprocess
import sys
import textwrap

import pytest
import wadler_lindig as wl

from wadler_lindig_parts import (
    PPart,
    pparts,
    pspec,
    register_alias,
    ReprMixin,
    unregister_alias,
)
from wadler_lindig_parts.examples import Version


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
    assert "\n" not in long._repr_html_()
    assert "\n" not in long._repr_latex_()


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
