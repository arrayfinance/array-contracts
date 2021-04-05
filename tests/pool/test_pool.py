import pytest


@pytest.fixture( scope='module', autouse=True )
def dai(interface):
    yield interface.ERC20( '0x6b175474e89094c44da98b954eedeac495271d0f' )


@pytest.fixture( scope='module', autouse=True )
def usdc(interface):
    yield interface.ERC20( '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' )


@pytest.fixture( scope='module', autouse=True )
def wbtc(interface):
    yield interface.ERC20( '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599' )


@pytest.fixture( scope='module', autouse=True )
def renbtc(interface):
    yield interface.ERC20( '0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D' )


@pytest.fixture( scope='module', autouse=True )
def weth(interface):
    yield interface.weth9( '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' )


@pytest.fixture( scope='module', autouse=True )
def pool():
    from scripts.create_smartpool import main
    # returns the smart pool that we create in the script
    yield main()


@pytest.fixture( scope='module', autouse=True )
def bpool(pool, interface):
    # returns the balancer pool that the smart pool contains
    yield interface.bpool( pool.bPool() )


# puts 100 lp tokens in and gets some DAI out
def test_lpin(someguy, accounts, pool, dai):
    accounts.default = someguy
    before = dai.balanceOf( someguy )
    tx = pool.exitswapPoolAmountIn( dai.address, 100, 0 )
    after = dai.balanceOf( someguy )
    # check that the dai was added to user
    assert tx.return_value == after - before


# puts 100 DAI in and gets some pool tokens out
def test_pool_in(someguy, accounts, pool, dai):
    accounts.default = someguy
    before = pool.balanceOf( someguy )
    tx = pool.joinswapExternAmountIn( dai.address, 100 * 1e18, 0 )
    after = pool.balanceOf( someguy )
    assert tx.return_value == after - before


def test_pool_supply(pool):
    ts = round( pool.totalSupply() / 1e23, 2 )
    assert ts == 3.33


def test_pool_value(pool):
    from scripts.create_smartpool import get_bpool, calc_bal, dm
    bp = get_bpool( pool )
    value = round( calc_bal( bp, dm ) / 1e23, 2 )
    assert value == 7.00
