"""Tests for the dataclass field layout: `pfields` and the routes built on it."""

import dataclasses

import pytest
import wadler_lindig as wl

from wadler_lindig_parts import (
    fields_to_parts,
    fields_to_pdoc,
    pfields,
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


def test_pfields_matches_wadler_lindig_dataclass_layout() -> None:
    assert wl.pformat(P(1.0)) == "P(x=1.0, tags=[])"
    names = tuple(name for name, _ in pfields(P(1.0)))
    assert names == ("x", "tags")


def test_pfields_rejects_non_dataclass() -> None:
    with pytest.raises(TypeError, match="not a dataclass"):
        pfields(object())


def test_pfields_rejects_a_dataclass_type() -> None:
    with pytest.raises(TypeError, match="not a dataclass"):
        pfields(P)


def test_pfields_registration_overrides() -> None:
    @dataclasses.dataclass
    class Q:
        a: int
        b: int

    @pfields.dispatch
    def _(obj: Q, /, **kw: object) -> tuple[tuple[str, object], ...]:
        return (("a", obj.a),)

    assert pfields(Q(1, 2)) == (("a", 1),)


# ---------------------------------------------------------------------------
# The parts layout for dataclasses


@dataclasses.dataclass
class Box:
    t: Term
    label: str


def test_plain_dataclass_product_layout() -> None:
    assert pspec(Point(1.0, 2.0), "product") == "Point(x=1.0, y=2.0)"


def test_value_spec_reaches_float_fields() -> None:
    assert pspec(Point(1.0, 2.0), ".2f") == "Point(x=1.00, y=2.00)"


def test_nested_registered_value_gets_markup() -> None:
    assert (
        pspec(Box(Term(1.0, "x"), "a"), "html")
        == "Box(t=<span>1.0</span> <span>x</span>, label=<span>a</span>)"
    )


def test_nested_registered_value_gets_value_spec() -> None:
    assert pspec(Box(Term(1.0, "x"), "a"), ".2f") == "Box(t=1.00 x, label=a)"


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


def test_unregistered_product_reprmixin_still_raises() -> None:
    @dataclasses.dataclass(repr=False)
    class Unregistered(ReprMixin):
        value: object

        __repr_spec__ = "mul"

    with pytest.raises(TypeError, match="registers no pparts"):
        pparts(Unregistered(1.0))


def test_non_dataclass_value_spec_still_raises() -> None:
    with pytest.raises(TypeError, match="does not support a value format spec"):
        pspec(object(), ".2f")


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
    assert pspec(Parent("a", Child("a")), "product") == "Parent(u=a, c=Child())"
    assert repr(Parent("a", Child("b"))) == "Parent(u='a', c=Child(u='b'))"


def test_nested_parents_pass_their_own_context() -> None:
    # The inner Parent receives parent_u="a" and must replace it with "b".
    outer = Parent("a", Parent("b", Child("b")))  # type: ignore[arg-type]
    assert repr(outer) == "Parent(u='a', c=Parent(u='b', c=Child()))"
    assert pspec(outer, "product") == "Parent(u=a, c=Parent(u=b, c=Child()))"


# ---------------------------------------------------------------------------
# Notebook markup for call types


def test_call_type_notebook_default_unchanged() -> None:
    assert C(2.0)._repr_html_() is None
    assert C(2.0)._repr_latex_() is None


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
# Audit fixes


@dataclasses.dataclass(repr=False)
class Unset(ReprMixin):
    __repr_spec__ = "call"
    a: int
    b: int = dataclasses.field(init=False)


def test_unset_field_prints_uninitialised_on_both_routes() -> None:
    assert repr(Unset(1)) == "Unset(a=1, b=<uninitialised>)"
    assert pspec(Unset(1), "product") == "Unset(a=1, b=<uninitialised>)"


def test_value_spec_leaves_bool_and_int_fields_alone() -> None:
    @dataclasses.dataclass
    class A:
        x: float
        flag: bool
        n: int

    assert pspec(A(1.234, True, 100), ".2f") == "A(x=1.23, flag=True, n=100)"
