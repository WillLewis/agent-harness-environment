from core.money import split_bill

def test_split_distributes_remainder():
    r = split_bill(100, 3)
    assert sum(r) == 100
    assert max(r) - min(r) <= 1
