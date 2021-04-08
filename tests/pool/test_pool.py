import pytest


@pytest.fixture( scope='module', autouse=True )
def pool():
    from scripts.setup import spool
    # returns the smart pool that we create in the script
    yield spool


@pytest.fixture( scope='module', autouse=True )
def bpool(pool, interface):
    # returns the balancer pool that the smart pool contains
    yield interface.bpool( pool.bPool() )


# puts 100 DAI in and gets some pool tokens out
def test_pool_in(someguy, accounts, pool, dai, whale):
    accounts.default = someguy
    dai.transfer( someguy, 100 * 1e18, {'from': whale.dai} )
    before = pool.balanceOf( someguy )
    dai.approve( pool, 100e18 )
    tx = pool.joinswapExternAmountIn( dai.address, 100 * 1e18, 0 )
    after = pool.balanceOf( someguy )
    assert tx.return_value == after - before


def test_pool_supply(pool):
    ts = round( pool.totalSupply() / 1e23, 2 )
    assert ts == 3.33


def test_pool_value(pool):
    from scripts.create_smartpool import get_bpool, calc_bal
    bp = get_bpool( pool )
    value = round( calc_bal( bp ) / 1e5, 2 )
    assert value == 7.00
