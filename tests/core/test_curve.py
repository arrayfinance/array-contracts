import pytest
import brownie
import math


@pytest.fixture(scope='module')
def spool(interface, daomsig):
    spool = interface.pool(
        '0xA800cDa5f3416A6Fb64eF93D84D6298a685D190d')
    spool.setCap(2 ** 256 - 1, {'from': daomsig})
    yield spool


@pytest.fixture(scope='module')
def bpool(interface):
    yield interface.bpool(
        '0x02e1300A7E6c3211c65317176Cf1795f9bb1DaAb')


@pytest.fixture(scope='module')
def roles(ArrayRoles, developer, timelock, daomsig):
    yield ArrayRoles.deploy(developer, timelock, {'from': daomsig})


@pytest.fixture(scope='module')
def af(ArrayFinance, spool, roles, daomsig):
    af = ArrayFinance.deploy(roles, {'from': daomsig})
    spool.approve(af, 2 ** 256 - 1, {'from': daomsig})
    af.sendInitLpToken({'from': daomsig})
    yield af


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# check for initial values OK
def test_setup(af, spool):
    assert spool.balanceOf(af) == 100e18
    assert af.totalSupply() == 10000e18


# check if access control modifier works,
# only daomsig should be able to call this - reverts
def test_access_control(af, user):
    with brownie.reverts():
        af.sendInitLpToken({'from': user})


# check if buy and sell function updates all required balances
# on all accounts
@pytest.mark.parametrize('amount', [10e18, 20e18, 40e18])
def test_buy_sell(amount, af, spool, bpool, devmsig, daomsig, rich, weth):
    supply_before = af.totalSupply()
    lpsupply_before = spool.totalSupply()
    weth.approve(af, 2 ** 256 - 1, {'from': rich})
    tx = af.buy(weth, amount, 10, {'from': rich})
    arraytokens = tx.return_value
    assert af.totalSupply() == arraytokens + supply_before
    assert af.balanceOf(rich) == arraytokens
    assert weth.balanceOf(daomsig) > 0.19 * amount
    assert weth.balanceOf(devmsig) > 0.09 * amount

    tx = af.sell['bool'](True, {'from': rich})

    # array tokens should be burned
    assert af.totalSupply() == supply_before

    # lp tokens given in exchange for array tokens
    assert math.floor(spool.totalSupply() / 1e18) == math.floor((lpsupply_before + tx.return_value) / 1e18)
