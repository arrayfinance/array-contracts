import pytest
from brownie import *

if network.is_connected():
    network.disconnect(kill_rpc=True)
    network.connect('geth-node')


@pytest.fixture(scope='module')
def developer(accounts):
    yield accounts[0]


@pytest.fixture(scope='module')
def governance(accounts):
    yield accounts[1]


@pytest.fixture(scope='module')
def user(accounts):
    yield accounts[2]


@pytest.fixture(scope='module')
def rogue(accounts):
    yield accounts[3]


@pytest.fixture(scope='module')
def guy(accounts):
    yield accounts[4]


@pytest.fixture(scope='module')
def daomsig(accounts):
    yield accounts.at('0xB60eF661cEdC835836896191EDB87CC025EFd0B7', force=True)


@pytest.fixture(scope='module')
def devmsig(accounts):
    yield accounts.at('0x3c25c256E609f524bf8b35De7a517d5e883Ff81C', force=True)


@pytest.fixture(scope='module')
def mock(Mock, developer):
    yield Mock.deploy({'from': developer})


@pytest.fixture(scope='module')
def timelock(governance, developer, user, ArrayTimelock):
    mindelay = 24 * 60 * 60  # one day
    yield ArrayTimelock.deploy(mindelay, [governance], [developer, user], {'from': developer})


@pytest.fixture(scope='module')
def dai(interface):
    yield interface.ERC20('0x6b175474e89094c44da98b954eedeac495271d0f')


@pytest.fixture(scope='module')
def usdc(interface):
    yield interface.ERC20('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')


@pytest.fixture(scope='module')
def weth(interface):
    yield interface.weth9('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')


@pytest.fixture(scope='module')
def wbtc(interface):
    yield interface.ERC20('0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599')


@pytest.fixture(scope='module')
def renbtc(interface):
    yield interface.ERC20('0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D')


@pytest.fixture(scope='module')
def poly(accounts):
    yield accounts.at('0x40ec5B33f54e0E8A33A975908C5BA1c14e5BbbDf', force=True)


@pytest.fixture(scope='module')
def nance(accounts):
    yield accounts.at('0x28C6c06298d514Db089934071355E5743bf21d60', force=True)


@pytest.fixture(scope='module')
def nance_two(accounts):
    yield accounts.at('0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE', force=True)


@pytest.fixture(scope='module')
def nance_three(accounts):
    yield accounts.at('0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8', force=True)


@pytest.fixture(scope='module')
def ftx(accounts):
    yield accounts.at('0x2FAF487A4414Fe77e2327F0bf4AE2a264a776AD2', force=True)


@pytest.fixture(scope='module')
def rex(accounts):
    yield accounts.at('0xFBb1b73C4f0BDa4f67dcA266ce6Ef42f520fBB98', force=True)


@pytest.fixture(scope='module')
def rich(guy, dai, usdc, weth, wbtc, renbtc, nance, poly, nance_two,
         interface, nance_three, ftx, rex):
    poly.transfer(guy, poly.balance())
    nance.transfer(guy, nance.balance())

    weth.deposit({'from': guy, 'value': guy.balance()})

    for _ in [dai, usdc, weth, wbtc, renbtc]:
        _.transfer(guy, _.balanceOf(nance), {'from': nance})
        _.transfer(guy, _.balanceOf(nance_two), {'from': nance_two})
        _.transfer(guy, _.balanceOf(nance_three), {'from': nance_three})
        _.transfer(guy, _.balanceOf(poly), {'from': poly})
        _.transfer(guy, _.balanceOf(ftx), {'from': ftx})
        _.transfer(guy, _.balanceOf(rex), {'from': rex})

    yield guy
