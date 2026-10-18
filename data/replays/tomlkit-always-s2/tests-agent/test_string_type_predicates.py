import pytest

from tomlkit.items import StringType


EXPECTED = {
    StringType.SLB: (True, False, True, False),
    StringType.MLB: (True, False, False, True),
    StringType.SLL: (False, True, True, False),
    StringType.MLL: (False, True, False, True),
}


@pytest.mark.parametrize("st", list(StringType))
def test_predicates(st):
    got = (st.is_basic(), st.is_literal(), st.is_singleline(), st.is_multiline())
    assert got == EXPECTED[st]
    assert all(isinstance(v, bool) for v in got)


def test_all_members_covered():
    assert set(EXPECTED) == set(StringType)
