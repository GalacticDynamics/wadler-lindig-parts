"""A parts layer over `wadler_lindig`.

One engine behind `repr`, `str`, `__format__` and the representations Jupyter
asks for. A type joins in by saying what it is *made of* -- a tree of roled
fragments returned from `pparts` -- and every output route lays that same tree
out its own way. Add a markup and every registered type gets it; register a
type and it gets every markup, including ones added later by somebody else.

The public surface is this module: `engine.__all__` plus `generic.__all__`,
plus the `examples` submodule. There is no private-but-documented tier, so a
consumer never needs an underscore name -- which matters, because across a
distribution boundary an underscore name can change in a patch release.

Examples
--------
>>> import wadler_lindig_parts as wlp
>>> from wadler_lindig_parts.examples import Version

>>> Version(2, 1)
2.1

>>> f"{Version(2, 1):html}"
'<span>2</span>.<span>1</span>'

>>> wlp.pparts(Version(2, 1))
(PPart(role='major', text='2', kind='content', doc=None),
 PPart(role='dot', text='.', kind='sep', doc=None),
 PPart(role='minor', text='1', kind='content', doc=None))

"""

from . import engine, examples, generic
from .engine import (
    ALIASES,
    AXES,
    Axis,
    bad_spec,
    doc_part,
    doc_to_str,
    FLAT,
    inert_axes,
    markup_table,
    MARKUPS,
    math_doc,
    parse_spec,
    parts_to_doc,
    parts_to_markup,
    PGroup,
    PPart,
    pparts,
    pparts_to_pdoc,
    pspec,
    register_alias,
    register_axis,
    render,
    ReprMixin,
    REQUIRED_MARKUP_KEYS,
    Spec,
    unregister_alias,
    unregister_axis,
    unwrap_math,
)
from .generic import pvalue, register_markup, SHORT_ARRAYS, unregister_markup


__all__ = ["examples", *engine.__all__, *generic.__all__]

# The names above are imported one by one rather than starred, so a name in a
# module's ``__all__`` that the module does not actually define is an
# ``ImportError`` here rather than a silently smaller public surface. That
# catches one direction of drift. The other -- a name added to a module's
# ``__all__`` and not to the import list above -- would leave ``__all__``
# promising a name this module lacks, so check it at import too.
_undelivered = sorted(name for name in __all__ if name not in globals())
if _undelivered:  # pragma: no cover -- an import-time guard, not a branch
    msg = (
        f"wadler_lindig_parts promises names it does not export: {_undelivered}. "
        "Add them to the import list in __init__.py."
    )
    raise ImportError(msg)
del _undelivered
