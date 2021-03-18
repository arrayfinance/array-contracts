import pytest
from rich.console import Console
import time

console = Console()


@pytest.fixture( scope='module', autouse=True )
def dai(interface):
    yield interface.ERC20( '0x6b175474e89094c44da98b954eedeac495271d0f' )


@pytest.fixture( scope='module', autouse=True )
def usdc(interface):
    yield interface.ERC20( '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' )


@pytest.fixture( scope='module', autouse=True )
def uni(interface):
    yield interface.router02( '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D' )


@pytest.fixture( autouse=True )
def isolation(fn_isolation):
    pass


@pytest.fixture
def pool(interface, someguy, accounts, uni, dai, usdc):
    accounts.default = someguy
    uni.swapExactETHForTokens( 0, [uni.WETH(), dai.address], someguy.address, int( time.time() ) + 1000,
                               {'from': someguy.address, 'value': '50 ether'} )

    uni.swapExactETHForTokens( 0, [uni.WETH(), usdc.address], someguy.address, int( time.time() ) + 1000,
                               {'from': someguy.address, 'value': '50 ether'} )
    PoolParams = ['ARRAYLP', 'Array LP', [usdc, dai], [1000e6, 1000e18], [25e18, 25e18], 1e14]
    PoolRights = [True, True, True, True, False, True]
    crpfact = interface.fact( '0xed52D8E202401645eDAD1c0AA21e872498ce47D0' )
    tx = crpfact.newCrp( '0x9424B1412450D0f8Fc2255FAf6046b98213B76Bd', PoolParams, PoolRights )
    poolcontract = interface.pool( tx.return_value )
    yield poolcontract


@pytest.fixture
def createdpool(someguy, pool, accounts, usdc, dai):
    accounts.default = someguy
    usdc.approve( pool.address, 2 ** 256 - 1 )
    dai.approve( pool.address, 2 ** 256 - 1 )
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
