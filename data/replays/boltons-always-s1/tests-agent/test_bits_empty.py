from boltons.mathutils import Bits


def test_empty_as_bin_hex_bytes():
    b = Bits('')
    assert len(b) == 0
    assert b.as_bin() == ''
    assert b.as_hex() == ''
    assert b.as_bytes() == b''
    assert b.as_list() == []


def test_empty_from_hex():
    assert Bits.from_hex('') == Bits('')
    assert Bits.from_hex(b'') == Bits('')
    assert Bits.from_hex('').len == 0


def test_empty_from_bytes_roundtrip():
    b = Bits.from_bytes(b'')
    assert b == Bits('')
    assert b.as_bytes() == b''
    assert Bits.from_bin(Bits('').as_bin()) == Bits('')
    assert Bits.from_hex(Bits('').as_hex()) == Bits('')


def test_nonempty_unchanged():
    assert Bits('0001').as_hex() == '01'
    assert Bits.from_hex('0x0f').as_bin() == '00001111'
    assert Bits.from_bytes(b'\x01\x02').as_bytes() == b'\x01\x02'
