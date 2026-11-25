"""Tests for the dataclass field layout: `pfields` and the routes built on it."""

import dataclasses

import pytest
import wadler_lindig as wl

from wadler_lindig_parts import pfields


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
