"""Make every example a test.

Constitution principle III: an example in a docstring or a Markdown page that
cannot run is a broken test, not stale prose. Sybil turns each one into its own
pytest item, reported against the line it lives on.

Two collectors, because the two file types carry examples differently:

- ``*.md`` -- fenced ``python`` blocks, parsed by `sybil.parsers.markdown`.
  Plain fences, deliberately: `unxt` uses `sybil.parsers.myst` because its
  pages carry ``{code-block}`` directives, and the MyST parsers would match
  nothing here.
- ``*.py`` -- ``>>>`` prompts in docstrings, parsed by
  `sybil.parsers.doctest`, which is the only parser that reaches docstring
  text rather than fenced blocks.

`ELLIPSIS` is needed because the engine's docstrings elide wadler-lindig
internals; `NORMALIZE_WHITESPACE` because a fragment tuple is wrapped across
lines for readability and the real `repr` is one line.
"""

from doctest import ELLIPSIS, NORMALIZE_WHITESPACE

from sybil import Sybil
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.markdown import PythonCodeBlockParser, SkipParser


optionflags = ELLIPSIS | NORMALIZE_WHITESPACE

docs = Sybil(
    parsers=[PythonCodeBlockParser(doctest_optionflags=optionflags), SkipParser()],
    patterns=["*.md"],
)
python = Sybil(
    parsers=[DocTestParser(optionflags=optionflags)],
    patterns=["*.py"],
)

pytest_collect_file = (docs + python).pytest()
