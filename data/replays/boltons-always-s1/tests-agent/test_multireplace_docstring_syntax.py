import ast
import re
import textwrap

from boltons.strutils import MultiReplace


def _usage_blocks():
    doc = MultiReplace.__doc__
    blocks = re.findall(r'Usage::\n\n((?: {8}.*\n)+)', doc)
    return [textwrap.dedent(b) for b in blocks]


def test_usage_examples_are_valid_python_and_run():
    blocks = _usage_blocks()
    assert len(blocks) == 2
    for block in blocks:
        ast.parse(block)
        ns = {}
        exec(block, ns)
        assert ns['new'] == 'The zoo bar hat ate a kraken'
        assert ns['new'] == ns['s'].sub('The foo bar cat ate a bat')


def test_iterable_example_has_balanced_kraken_literal():
    iterable = _usage_blocks()[1]
    assert "('bat', 'kraken')" in iterable
    assert "'kraken)'" not in iterable
