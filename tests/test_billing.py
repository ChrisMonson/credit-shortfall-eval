import pytest

from shortfall.billing import ReadResult, charge_read, read_cost


@pytest.mark.parametrize(
    ("characters", "cost"),
    [(1, 1), (999, 1), (1000, 1), (1001, 2), (2000, 2), (4500, 5), (7999, 8), (8000, 8)],
)
def test_read_cost(characters, cost):
    assert read_cost(characters) == cost


def test_a_read_the_balance_covers(make_account):
    account = make_account(117)
    assert charge_read(account, 4500) == ReadResult(ok=True, cost=5, balance=112, recharges=0)
    assert account.balance == 112


def test_a_read_that_uses_the_whole_balance(make_account):
    account = make_account(5)
    assert charge_read(account, 4500) == ReadResult(ok=True, cost=5, balance=0, recharges=0)


def test_a_read_the_balance_cannot_cover_is_refused(make_account):
    account = make_account(4)
    assert charge_read(account, 4500) == ReadResult(ok=False, cost=5, balance=4, recharges=0)
    assert account.balance == 4


def test_a_refused_read_does_not_change_the_account(make_account):
    account = make_account(4)
    before = account.to_dict()
    charge_read(account, 4500)
    assert account.to_dict() == before


def test_auto_recharge_covers_a_short_balance(make_account):
    account = make_account(4, auto_recharge=True)
    assert charge_read(account, 4500) == ReadResult(ok=True, cost=5, balance=499, recharges=1)
    assert account.balance == 499


def test_auto_recharge_from_zero(make_account):
    account = make_account(0, auto_recharge=True)
    assert charge_read(account, 2000) == ReadResult(ok=True, cost=2, balance=498, recharges=1)


def test_auto_recharge_does_not_charge_when_the_balance_covers_the_read(make_account):
    account = make_account(117, auto_recharge=True)
    assert charge_read(account, 4500).recharges == 0
    assert account.balance == 112


def test_auto_recharge_charges_as_many_times_as_it_takes(make_account):
    account = make_account(0, auto_recharge=True)
    assert charge_read(account, 1_200_000) == ReadResult(ok=True, cost=1200, balance=300, recharges=3)
