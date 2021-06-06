import pytest
import warnings
import brownie
from dotmap import DotMap
from brownie import *


@pytest.fixture(scope='module')
def pool():
    from scripts.deployer import Deployer
    d = Deployer()
    d.setup()
    yield d.pool


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# check if our pre-calc for array is rightk
def test_correct_calc_estimation(dai, accounts):
    accounts.default = governance
    amount = 1000 * 1e18

    dai.approve(, amount)
    calc = d.crv.calculateArrayTokensGivenERC20Tokens(dai, amount)
    tx = d.crv.buy(dai, amount, 2)

    assert calc == tx.return_value


def test_buy(d, accounts):
    accounts.default = d.me
    for k, v in d.tokens.items():
        prev = d.array.balanceOf(d.me)
        m = min(v.balanceOf(d.me), (d.bpool.getBalance(v.address)) / 3)
        tx = d.crv.buy(v.address, m, 2)
        aft = d.array.balanceOf(d.me)
        assert int(tx.return_value) == (aft - prev)


def test_revert_no_balance(d, accounts):
    accounts.default = accounts[0]
    buy = 1000e18
    coin = d.tokens['dai']
    coin.transfer(ZERO_ADDRESS, coin.balanceOf(accounts[0]))
    coin.approve(d.crv, buy)
    with brownie.reverts("user balance < amount"):
        d.crv.buy(coin, buy, 2, {'from': accounts[0]})


def test_gas(d, accounts):
    tx = d.crv.maxGasPrice()
    gas = tx.return_value + 1e8
    accounts.default = d.me
    with brownie.reverts('Must send equal to or lower than fast gas price to mitigate front running attacks.'):
        tx = d.crv.buy(d.tokens.dai, 100e18, 2, {'gas_price': gas})


def test_roles(d, accounts):
    with brownie.reverts('wrong role'):
        d.crv.setDaoPct(2 * 10 ** 6, {'from': accounts[1]})
    with brownie.reverts('wrong role'):
        d.crv.setDevPct(5 * 10 ** 6, {'from': accounts[1]})
    with brownie.reverts('wrong role'):
        d.crv.setMaxSupply(1e18, {'from': accounts[1]})

    assert d.crv.setDaoPct(2 * 10 ** 6, {'from': d.me})
    assert d.crv.setDevPct(5 * 10 ** 6, {'from': d.me})
    assert d.crv.setMaxSupply(1e18, {'from': d.me})


def test_set_pct(d, chain):
    accounts.default = d.me
    chain.snapshot()
    tx = d.crv.buy(d.tokens.dai, 1000 * 1e18, 2)
    purchase = tx.return_value

    chain.revert()
    d.crv.setDaoPct(30 * 10 ** 16)
    d.crv.setDaoPct(30 * 10 ** 16)
    tx = d.crv.buy(d.tokens.dai, 1000 * 1e18, 2)
    purchase_ = tx.return_value

    assert purchase_ < purchase
