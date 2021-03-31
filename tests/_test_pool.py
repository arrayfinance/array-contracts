import pytest
from dotmap import DotMap
from rich.console import Console
import time

console = Console()


@pytest.fixture( scope='module', autouse=True )
def dai(interface, someguy):
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
def richguy(someguy, dai, usdc, renbtc, wbtc, weth, whale):
    dai.transfer( someguy, 1e24, {'from': whale.dai} )
    usdc.transfer( someguy, 1e12, {'from': whale.usdc} )
    renbtc.transfer( someguy, 1e14, {'from': whale.renbtc} )
    wbtc.transfer( someguy, 1e14, {'from': whale.wbtc} )
    weth.deposit( 100e18, {'from': someguy} )
    yield someguy


@pytest.fixture( scope='module', autouse=True )
def tokens(renbtc, weth, wbtc, dai, usdc):
    yield [weth.address, wbtc.address, renbtc.address, dai.address, usdc.address]


@pytest.fixture( scope='module', autouse=True )
def uniswap_pairs(interface):
    p = DotMap()
    p.ren = interface.pair( '0x81fbef4704776cc5bba0a5df3a90056d2c6900b3' )
    p.wbtc = interface.pair( '0xBb2b8038a1640196FbE3e38816F3e67Cba72D940' )
    p.dai = interface.pair( '0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11' )
    p.usdc = interface.pair( '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc' )


@pytest.fixture( scope='module', autouse=True )
def prices(uniswap_pairs, interface):
    p = DotMap()
    for k, v in uniswap_pairs.items():
        token0 = interface.ERC20( v.token0() )
        token1 = interface.ERC20( v.token1() )
        r = v.getReserves()
        d = [token0.decimals(), token1.decimals()]
        # check that the token we divide by is eth
        if token0.symbol().lower() == 'weth':
            i, j = 1, 0
        else:
            i, j = 0, 1
        result = (r[i] / 10 ** d[i]) / (r[j] / 10 ** d[j])
        p[k] = result
    yield p


@pytest.fixture( scope='module', autouse=True )
def items(prices, renbtc, weth, wbtc, dai, usdc):
    dm = DotMap()
    amount = 100

    dm.contracts.weth = weth
    dm.contracts.wbtc = wbtc
    dm.contracts.renbtc = renbtc
    dm.contracts.dai = dai
    dm.contracts.usdc = usdc

    dm.weights.weth = 0.33
    dm.weights.wbtc = 0.165
    dm.weights.renbtc = 0.165
    dm.weights.dai = 0.17
    dm.weights.usdc = 0.17

    dm.prices.weth = 1
    dm.prices.wbtc = prices.wbtc
    dm.prices.renbtc = prices.renbtc
    dm.prices.dai = prices.dai
    dm.prices.usdc = prices.usdc

    dm.balances.weth = dm.weights.weth * dm.prices.weth * amount * 1e18
    dm.balances.wbtc = dm.weights.wbtc * dm.prices.wbtc * amount * 1e8
    dm.balances.renbtc = dm.weights.renbtc * dm.prices.renbtc * amount * 1e8
    dm.balances.dai = dm.weights.dai * dm.prices.dai * amount * 1e18
    dm.balances.usdc = dm.weights.usdc * dm.prices.usdc * amount * 1e6

    yield dm


@pytest.fixture( autouse=True )
def isolation(fn_isolation):
    pass


@pytest.fixture
def pool(richguy, dm, accounts, interface):

    accounts.default = richguy
    tokens = [_.address for _ in dm.contracts]
    balances = [_ for _ in dm.balances.values()]

    weights = [_/2.5 for _ in dm.weights.values()]

    PoolParams = ['ARRAYLP', 'Array LP', tokens, balances, weights, 1e14]
    PoolRights = [True, True, True, True, False, True]
    crpfact = interface.fact( '0xed52D8E202401645eDAD1c0AA21e872498ce47D0' )
    tx = crpfact.newCrp( '0x9424B1412450D0f8Fc2255FAf6046b98213B76Bd', PoolParams, PoolRights )
    poolcontract = interface.pool( tx.return_value )

    yield poolcontract


@pytest.fixture
def createdpool(richguy, pool, accounts, dm):
    accounts.default = richguy

    for _ in dm.contracts.values():
        _.approve(pool.address, 2**256-1)

    pool.createPool( 1e20 )

    yield pool


def test_lpin(someguy, accounts, createdpool, dai):
    accounts.default = someguy
    before = dai.balanceOf( someguy )
    tx = createdpool.exitswapPoolAmountIn( dai.address, 100, 0 )
    after = dai.balanceOf( someguy )
    assert tx.return_value == after - before


def test_pool_in(someguy, accounts, createdpool, dai):
    accounts.default = someguy
    before = createdpool.balanceOf( someguy )
    tx = createdpool.joinswapExternAmountIn( dai.address, 100, 0 )
    after = createdpool.balanceOf( someguy )
    assert tx.return_value == after - before
