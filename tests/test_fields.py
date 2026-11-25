"""Tests for the dataclass field layout: `pfields` and the routes built on it."""

import dataclasses

import pytest
import wadler_lindig as wl

from wadler_lindig_parts import (
    fields_to_parts,
    fields_to_pdoc,
    pfields,
    PGroup,
    PPart,
    pparts,
    pspec,
    ReprMixin,
)
from wadler_lindig_parts.examples import Point, Term


@dataclasses.dataclass
class P:
    x: float
    y: float = 2.0
    tags: list = dataclasses.field(default_factory=list)
    hidden: int = dataclasses.field(default=0, repr=False)


# ---------------------------------------------------------------------------
# pfields


def test_pfields_hides_identity_defaults_and_repr_false() -> None:
    assert pfields(P(1.0)) == (("x", 1.0), ("tags", []))


def test_pfields_hide_defaults_false_shows_all_repr_fields() -> None:
    assert pfields(P(1.0), hide_defaults=False) == (
        ("x", 1.0),
        ("y", 2.0),
        ("tags", []),
    )


def test_pfields_rejects_non_dataclass() -> None:
    with pytest.raises(TypeError, match="not a dataclass"):
        pfields(object())


def test_pfields_rejects_a_dataclass_type() -> None:
    with pytest.raises(TypeError, match="not a dataclass"):
        pfields(P)


# ---------------------------------------------------------------------------
# The parts layout for dataclasses


@dataclasses.dataclass
class Box:
    t: Term
    label: str


def test_plain_dataclass_product_layout() -> None:
    assert pspec(Point(1.0, 2.0), "product") == "Point(x=1.0, y=2.0)"


def test_nested_registered_value_gets_markup() -> None:
    assert (
        pspec(Box(Term(1.0, "x"), "a"), "html")
        == "Box(t=<span>1.0</span> <span>x</span>, label=<span>&#x27;a&#x27;</span>)"
    )


def test_nested_registered_value_gets_value_spec() -> None:
    assert pspec(Box(Term(1.0, "x"), "a"), ".2f") == "Box(t=1.00 x, label='a')"


def test_unformattable_field_falls_back_to_text_under_spec() -> None:
    @dataclasses.dataclass
    class L:
        xs: list

    assert pspec(L([1, 2]), ".2f") == "L(xs=[1, 2])"


def test_nested_dataclass_gets_the_layout_and_the_spec() -> None:
    @dataclasses.dataclass
    class Outer:
        p: Point

    assert pspec(Outer(Point(1.0, 2.0)), ".1f") == "Outer(p=Point(x=1.0, y=2.0))"
    assert pspec(Outer(Point(1.0, 2.0)), ".2f") == "Outer(p=Point(x=1.00, y=2.00))"


def test_pfields_override_changes_the_parts_layout() -> None:
    @dataclasses.dataclass
    class R:
        a: int
        b: int

    @pfields.dispatch
    def _(obj: R, /, **kw: object) -> tuple[tuple[str, object], ...]:
        return (("b", obj.b),)

    assert pspec(R(1, 2), "product") == "R(b=2)"


def test_unregistered_call_reprmixin_dataclass_gets_field_layout() -> None:
    @dataclasses.dataclass(repr=False)
    class C(ReprMixin):
        __repr_spec__ = "call"
        v: float

    assert pspec(C(1.0), "product") == "C(v=1.0)"


def test_cyclic_dataclass_raises_cleanly() -> None:
    @dataclasses.dataclass
    class N:
        nxt: object = None

    n = N()
    n.nxt = n
    with pytest.raises(TypeError, match="contains itself"):
        pspec(n, "product")


# ---------------------------------------------------------------------------
# The constructor route


@dataclasses.dataclass(repr=False)
class C(ReprMixin):
    __repr_spec__ = "call"
    v: float
    w: float = 1.0


def test_call_repr_matches_plain_dataclass_layout() -> None:
    assert repr(C(2.0)) == "C(v=2.0)"


def test_super_pdoc_returns_a_document_under_call() -> None:
    assert isinstance(C(2.0).__pdoc__(), wl.AbstractDoc)


@dataclasses.dataclass(repr=False)
class D(ReprMixin):
    __repr_spec__ = "call"
    a: int
    b: int


@pfields.dispatch
def _(obj: D, /, **kw: object) -> tuple[tuple[str, object], ...]:
    return (("a", obj.a),)


def test_pfields_override_changes_repr_and_product_together() -> None:
    assert repr(D(1, 2)) == "D(a=1)"
    assert pspec(D(1, 2), "product") == "D(a=1)"


@dataclasses.dataclass(repr=False)
class Child(ReprMixin):
    __repr_spec__ = "call"
    u: str


@pfields.dispatch
def _(obj: Child, /, **kw: object) -> tuple[tuple[str, object], ...]:
    return () if kw.get("parent_u") == obj.u else (("u", obj.u),)


@dataclasses.dataclass(repr=False)
class Parent(ReprMixin):
    """Passes its ``u`` to its child on both routes, as a galax composite will."""

    __repr_spec__ = "call"
    u: str
    c: Child

    def __pdoc__(self, **kw: object) -> wl.AbstractDoc:
        # Merge, so a parent nested in another parent overrides its context.
        kw = {**kw, "parent_u": self.u}
        return fields_to_pdoc(self, pfields(self, **kw), **kw)


@pparts.dispatch
def _(obj: Parent, /, *, markup: str = "text", **kw: object) -> tuple:
    kw = {**kw, "parent_u": obj.u}
    return fields_to_parts(obj, pfields(obj, **kw), markup=markup, **kw)


def test_parent_context_keyword_reaches_child_pfields_on_both_routes() -> None:
    assert repr(Parent("a", Child("a"))) == "Parent(u='a', c=Child())"
    assert pspec(Parent("a", Child("a")), "product") == "Parent(u='a', c=Child())"
    assert repr(Parent("a", Child("b"))) == "Parent(u='a', c=Child(u='b'))"


def test_nested_parents_pass_their_own_context() -> None:
    # The inner Parent receives parent_u="a" and must replace it with "b".
    outer = Parent("a", Parent("b", Child("b")))  # type: ignore[arg-type]
    assert repr(outer) == "Parent(u='a', c=Parent(u='b', c=Child()))"
    assert pspec(outer, "product") == "Parent(u='a', c=Parent(u='b', c=Child()))"


# ---------------------------------------------------------------------------
# Notebook markup for call types


@dataclasses.dataclass(repr=False)
class E(ReprMixin):
    __repr_spec__ = "call"
    __notebook_parts__ = True
    t: Term


def test_notebook_parts_switch_shows_markup() -> None:
    e = E(Term(1.0, "x"))
    assert e._repr_html_() == pspec(e, "html")
    assert e._repr_latex_() == pspec(e, "latex")
    assert e._repr_latex_().startswith("$")
    assert repr(e) == "E(t=1.0 * x)"


# ---------------------------------------------------------------------------
# Values inside the layout


@dataclasses.dataclass(repr=False)
class Unset(ReprMixin):
    __repr_spec__ = "call"
    a: int
    b: int = dataclasses.field(init=False)


def test_unset_field_prints_uninitialised_on_both_routes() -> None:
    assert repr(Unset(1)) == "Unset(a=1, b=<uninitialised>)"
    assert pspec(Unset(1), "product") == "Unset(a=1, b=<uninitialised>)"


def test_value_spec_formats_only_non_integer_numbers() -> None:
    import datetime
    import enum

    class Color(enum.IntEnum):
        RED = 1

    @dataclasses.dataclass
    class M:
        x: float
        when: datetime.date
        name: str
        c: Color
        flag: bool

    when = datetime.date(2024, 1, 2)
    m = M(1.23456, when, "galactic", Color.RED, True)
    want = f"M(x=1.23, when={when}, name='galactic', c={Color.RED}, flag=True)"
    assert pspec(m, ".2f") == want
    assert pspec(m, ".3") == want


def test_string_fields_print_quoted() -> None:
    @dataclasses.dataclass
    class S:
        s: str

    assert pspec(S("a, b=c"), "product") == "S(s='a, b=c')"
    assert pspec(S(""), "product") == "S(s='')"


def test_a_mistyped_spec_raises_on_a_dataclass() -> None:
    with pytest.raises(ValueError, match="not a valid Python format spec"):
        pspec(Point(1.5, 2.0), "latx")


class Sym(str):
    pass


@pparts.dispatch
def _(obj: Sym, /, *, markup: str = "text", **kw: object) -> tuple:
    return (PPart("sym", "alpha"),)


def test_a_str_subclass_with_its_own_pparts_uses_it() -> None:
    @dataclasses.dataclass
    class H:
        s: Sym
        t: str

    assert pspec(H(Sym("a"), "a"), "product") == "H(s=alpha, t='a')"


def test_fields_without_pparts_print_their_str() -> None:
    import pathlib

    @dataclasses.dataclass
    class Misc:
        p: pathlib.PurePosixPath

    assert pspec(Misc(pathlib.PurePosixPath("a/b")), "product") == "Misc(p=a/b)"


class Ctor(ReprMixin):
    """A call-spec mixin type that is not a dataclass, with its own __pdoc__."""

    __repr_spec__ = "call"

    def __init__(self, n: int) -> None:
        self.n = n

    def __pdoc__(self, **kw: object) -> wl.AbstractDoc:
        return wl.TextDoc(f"Ctor({self.n})")


def test_call_mixin_non_dataclass_field_prints_its_repr() -> None:
    @dataclasses.dataclass
    class W:
        t: Ctor

    assert pspec(W(Ctor(3)), "product") == "W(t=Ctor(3))"


def test_a_spec_that_is_not_a_python_format_spec_raises_up_front() -> None:
    import datetime

    # A strftime pattern is not a format spec a number accepts.
    with pytest.raises(ValueError, match="not a valid Python format spec"):
        pspec(Term(datetime.date(2024, 1, 2), "x"), "%Y")


class Wide(ReprMixin):
    """A call-spec non-dataclass whose own __pdoc__ is a breakable document."""

    __repr_spec__ = "call"

    def __init__(self, *items: str) -> None:
        self.items = items

    def __pdoc__(self, **kw: object) -> wl.AbstractDoc:
        return wl.bracketed(
            begin=wl.TextDoc("Wide("),
            docs=[wl.pdoc(x) for x in self.items],
            sep=wl.comma,
            end=wl.TextDoc(")"),
            indent=2,
        )


def test_nested_call_mixin_follows_the_parent_layout() -> None:
    @dataclasses.dataclass
    class Box:
        name: str
        c: object

    w = Wide(*(["x" * 30] * 4))
    flat = f"Box(name='bx', c=Wide({', '.join([repr('x' * 30)] * 4)}))"
    assert pspec(Box("bx", w), "product-width=200") == flat


def test_call_mixin_ignores_a_value_spec() -> None:
    assert pspec(Wide("a"), ".2f") == pspec(Wide("a"), "product")


class Marker:
    pass


@pparts.dispatch
def _(obj: list[Marker], /, *, markup: str = "text", **kw: object) -> tuple:
    return (PPart("markers", f"{len(obj)} markers"),)


def test_instance_dispatch_reaches_parametric_registrations() -> None:
    @dataclasses.dataclass
    class D:
        a: list

    assert pspec(D([Marker(), Marker()]), "product") == "D(a=2 markers)"


def test_a_number_that_rejects_the_spec_falls_back() -> None:
    import fractions

    @dataclasses.dataclass
    class F:
        q: fractions.Fraction
        x: float

    assert pspec(F(fractions.Fraction(1, 3), 1.23456), ".3") == "F(q=1/3, x=1.23)"


class Parted(ReprMixin):
    """A call-spec non-dataclass with its own __pdoc__ *and* its own pparts."""

    __repr_spec__ = "call"
    __notebook_parts__ = True

    def __init__(self, v: float) -> None:
        self.v = v

    def __pdoc__(self, **kw: object) -> wl.AbstractDoc:
        return wl.TextDoc(f"Parted({self.v})")


@pparts.dispatch
def _(
    obj: Parted, /, *, markup: str = "text", value_spec: str | None = None, **kw: object
) -> tuple:
    return (PPart("v", format(obj.v, value_spec or "")),)


def test_a_call_mixin_with_its_own_pparts_uses_them_as_a_field() -> None:
    @dataclasses.dataclass
    class D:
        x: Parted

    assert pspec(D(Parted(1.23456)), ".2f") == "D(x=1.23)"


class Unit:
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Unit({self.name!r})"


@dataclasses.dataclass(repr=False)
class Qty(ReprMixin):
    """A container that forwards **kw to an unregistered child, per the docs."""

    __repr_spec__ = "mul"
    v: float
    unit: Unit


@pparts.dispatch
def _(obj: Qty, /, *, markup: str = "text", **kw: object) -> tuple:
    return (
        PPart("v", str(obj.v)),
        PPart("mul", " * ", "sep"),
        PGroup("unit", pparts(obj.unit, markup=markup, **kw)),
    )


def test_only_the_field_value_counts_as_nested() -> None:
    @dataclasses.dataclass
    class Box:
        q: Qty

    q = Qty(1.5, Unit("km"))
    assert pspec(q, "product") == "1.5 km"
    assert pspec(Box(q), "product") == "Box(q=1.5 km)"


class System:
    """A registered type with no value to format, like a unit system."""


@pparts.dispatch
def _(obj: System, /, *, markup: str = "text", **kw: object) -> tuple:
    return (PPart("system", "galactic"),)


def test_a_field_with_no_value_to_format_ignores_the_spec() -> None:
    @dataclasses.dataclass
    class Pot:
        m: float
        units: System

    assert pspec(Pot(1.23456, System()), ".2f") == "Pot(m=1.23, units=galactic)"
    assert pspec(System(), ".2f") == "galactic"


# ---------------------------------------------------------------------------
# Ordinary registrations


def test_a_registration_on_a_dataclass_beats_the_layout() -> None:
    @dataclasses.dataclass
    class Own:
        a: int

    @pparts.dispatch
    def _(obj: Own, /, *, markup: str = "text", **kw: object) -> tuple:
        return (PPart("own", "mine"),)

    assert pspec(Own(1), "product") == "mine"


def test_dataclass_type_excludes_reprmixin() -> None:
    from wadler_lindig_parts import Dataclass

    assert isinstance(Point(1.0, 2.0), Dataclass)
    assert not isinstance(C(1.0), Dataclass)
    assert not isinstance(Point, Dataclass)


def test_strings_and_numbers_are_ordinary_registrations() -> None:
    assert pspec("a, b=c", "product") == "'a, b=c'"
    assert pspec(1.23456, ".2f") == "1.23"
    assert pspec(3, ".2f") == "3"


def test_layout_roles_do_not_collide_with_markup_role_overrides() -> None:
    from wadler_lindig_parts import MARKUPS, register_markup, unregister_markup

    styled = {"name": "<b>{}</b>", "key": "_{}_", "comma": "?", "close": "!"}
    register_markup("styled", {**MARKUPS["text"], **styled})
    try:
        assert pspec(Point(1.0, 2.0), "styled") == "Point(x=1.0, y=2.0)"
    finally:
        unregister_markup("styled")
