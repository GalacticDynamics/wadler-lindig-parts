# Why formatting is one engine

There are four ways to turn a value into a string: `repr`, `str`,
`__format__`, and the representations Jupyter asks for. They share one spec
vocabulary and one entry point, and most of them share the renderer as well.
The constructor form `repr` produces is the exception, for reasons below. This
page is about why that is worth doing and what it cost.

For the spec vocabulary itself, see [the grammar](../index.md). To make a type
of your own formattable, see
[How to make your own type formattable](../how-to/make-a-type-formattable.md).

## Why one renderer and not four

Four renderers means four places a change has to land, and nothing to stop
them drifting. That is not hypothetical. Before this engine existed, in the
library this package was extracted from, `_repr_latex_` wrapped a unit's
`repr` in `$…$` by slicing the first and last character off it. For a plain
unit that worked. For a value whose `repr` was not already `$…$` it quietly
ate two real characters. The fault was structural: the LaTeX path had no way
to know what the other three knew, so nothing kept it in step with them.

So a type no longer says how it renders. It says what it is _made of_: a tree
of labelled fragments, returned from `pparts`. Each output route lays that
same tree out differently. Add a markup and every type gets it. Register a
type and it gets every markup, including ones added later by somebody else.

```python
>>> from wadler_lindig_parts.examples import Version

>>> repr(Version(2, 1)), f"{Version(2, 1):html}", f"{Version(2, 1):latex}"
('2.1', '<span>2</span>.<span>1</span>', '$2.1$')

```

One `pparts` method produced all three. The slicing bug has nowhere to live:
nothing in the LaTeX path knows what a character is.

The cost is indirection. Reading `_repr_latex_` used to show you the whole
story; now it shows you a call into a renderer, and the story is spread across
the fragment tree, the markup table and the layout. That is a real loss, paid
once, against four paths that can no longer disagree.

## Why the spec grammar scans left to right

A spec is a run of keywords that may end in a Python format spec:
`mul-html-.2f`. The obvious way to parse that is to split on `-` and sort the
pieces into keywords and leftovers. It does not work, because a Python format
spec can contain `-` itself — as a sign flag in `-.2f`, or as a fill character
in `->10.2f`. Split on `-` and `->10.2f` becomes two tokens, neither of which
means anything.

So the scan is strictly left to right and stops looking for keywords at the
first token that is not one. Everything after that point is the format spec,
`-` and all. No token needs to be examined for what it might be; its position
settles it.

```python
>>> from wadler_lindig_parts import parse_spec

>>> parse_spec("mul-->10.2f")["value"]
'->10.2f'

```

The price is one rule the reader has to carry: the format spec goes last.
`mul-.2f-html` does not fail with "unexpected keyword after format spec" — it
cannot, because by then there are no keywords, only the string `.2f-html`,
which is simply not a valid format spec. The alternative designs are worse: a
delimiter other than `-` would make the common cases uglier, and sniffing each
token for format-spec-ness would make adding a keyword able to change what an
existing spec means.

## Why keywords share one namespace

`latex` names a markup. `mul` names a separator style. Neither says which axis
it belongs to, so a run can be written in any order: `html-mul` and `mul-html`
are the same request.

The cost arrives when two packages want one word. `dim` could as reasonably
mean a unit's dimension or a manifold's dimensionality. Both readings are
right, and a flat namespace cannot hold both.

The way out is that `axis=word` is always available, and is in fact the real
form: a keyword _sets an axis to a value_, so `units_dim=dim` is the operation
spelled out and bare `dim` is shorthand for it. A bare word resolves while
exactly one axis claims it; when two do, it raises and names both ways to
disambiguate. Because that is per token, a collision costs one word in one
spec — `latex-mul-units_dim=dim-.3f` — rather than a rewrite. A package that
expects to share vocabulary can write the explicit form from the start and
never be affected.

Note what this rules out. Refusing the *second registration* would be louder,
and it is tempting now that the registrants are separate distributions. But
then there is no second axis for `axis=word` to resolve to, and a shared word
becomes a defeat rather than an inconvenience. The ambiguity is held open on
purpose.

The alternative, namespacing every keyword by its axis from the beginning,
would have made every ordinary spec longer to pay for a collision that has not
happened yet.

## Why the constructor form is not built from fragments

Every rendering but one is assembled from the fragments a type reports through
`pparts`. The `call` layout is the exception: it hands off to
`wadler_lindig.pformat`, which uses the type's own `__pdoc__`.

The two forms answer different questions. `product` layout shows what a value
**is** — `2.0 * x`. The `call` layout shows how to **rebuild** it —
`Term(coeff=2.0, symbol='x')`. Only the type knows the second, and knowing it
takes more than knowing how the value looks.

`Point` is the clearest case. It registers no `pparts` and inherits no mixin —
it has told this engine nothing at all:

```python
>>> import dataclasses
>>> from wadler_lindig_parts import pspec
>>> from wadler_lindig_parts.examples import Point

>>> dataclasses.is_dataclass(Point)
True
>>> pspec(Point(1.0, 2.0), "call")
'Point(x=1.0, y=2.0)'

```

That worked because `wadler_lindig` gives a dataclass a usable `__pdoc__` for
free, and the `call` layout delegates to it. A renderer working from display
fragments could not have produced it: it would have had to know that `Point`
takes `x` and `y` by keyword, in that order, under those names — which is
constructor knowledge, not display knowledge.

The delegation has a consequence worth being explicit about: `call` layout
asks for `__pdoc__`, and `ReprMixin` *supplies* a `__pdoc__` built from
fragments. So a type using the mixin gets the fragment form under `call` too,
while a plain dataclass gets the constructor form:

```python
>>> from wadler_lindig_parts.examples import Term

>>> pspec(Term(2.0, "x"), "call")       # ReprMixin's own __pdoc__
'2.0 * x'
>>> pspec(Point(1.0, 2.0), "call")      # wadler-lindig's dataclass __pdoc__
'Point(x=1.0, y=2.0)'

```

That is not an inconsistency; it is the delegation working. `call` means "ask
the type", and the two types answer differently because they have told
`wadler_lindig` different things. A type whose `repr` should be a constructor
expression writes its own `__pdoc__` and does not use the mixin's.

So `eval(repr(x)) == x` stays a promise each type keeps for itself rather than
one the renderer makes on every type's behalf. The names in such a repr have
to be in scope for `eval` to resolve them, which is a constraint only the type
can reason about.

## Why an inert axis is allowed to do nothing

A spec can be accepted and change nothing. Asking for `mul` on a `Version`
still renders `2.1`, because a version's own `.` separator is a `sep` fragment
and the `sep` axis leaves those alone:

```python
>>> f"{Version(2, 1):mul}"
'2.1'
>>> f"{Version(2, 1):bare}"
'2.1'

```

This could have been an error, and there is a case for it: a spec that does
nothing is usually a mistake, and silence is how mistakes survive. But erroring
would break composite types, which depend on that same forwarding. An
`Interval` of two `Term`s does not know the `value` axis exists; it passes the
axes it does not handle down to its parts, and a format spec reaches the
nested terms. A type cannot declare in advance which axes it honours, because
the honest answer depends on the value.

So whether an axis mattered is settled by experiment rather than by
declaration — render again with the axis reset to its default and see whether
the output moves. `inert_axes` does exactly that:

```python
>>> from wadler_lindig_parts import inert_axes, parse_spec, render

>>> spec = parse_spec("mul")
>>> inert_axes(Version(2, 1), spec, render(Version(2, 1), spec))
['sep']

```

It reports `sep` because asking for `mul` genuinely changed nothing here. It
is a call you make while debugging rather than a setting, because each check
costs a second render.

## Why the engine is a package of its own

The code was split in two inside `unxt`, at the line where it would later be
cut. One half knew about fragments, markups, the parser, the layouts and the
axis registry, and nothing about quantities. The other half was the axes
`unxt` contributed to the grammar. This package is that first half, extracted.

The split existed because `coordinax` and `galax` needed the same machinery.
The alternative was for each to depend on `unxt` for its string formatting,
which would have made `unxt` a dependency of packages with nothing else to do
with units.

A claim like "imports nothing domain-specific" decays the moment someone adds
a convenient import, so it is enforced rather than written down: a test parses
every module in this package and fails if anything outside `wadler_lindig`,
`plum` and the standard library appears. There are exactly two runtime
dependencies, and adding a third means deleting that test, which a reviewer
sees.

`unxt`, `coordinax` and `galax` now register into this package as peers. There
is no privileged set of axes, and an axis added downstream is read out of a
spec exactly like a built-in one. What changed at the extraction was not the
mechanism but the status of three rules: the registry's collision behaviour,
the refusal of a malformed markup row, and the moment `__repr_spec__` is
resolved were implementation details inside one package, and are contract
between distributions now. Each has a test pinning it, for that reason.
