import pytest
from dotmap import DotMap


@pytest.fixture( scope="module", autouse=True )
def deployer(accounts):
    yield accounts[0]


@pytest.fixture( scope='module', autouse=True )
def someguy(accounts):
    yield accounts[1]


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
def whale(accounts):
    whale = DotMap()
    whale.dai = accounts.at( '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643', force=True )
    whale.usdc = accounts.at( '0x39aa39c021dfbae8fac545936693ac917d5e7563', force=True )
    whale.wbtc = accounts.at( '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4', force=True )
    whale.renbtc = accounts.at( '0x93054188d876f558f4a66B2EF1d97d16eDf0895B', force=True )
    yield whale
