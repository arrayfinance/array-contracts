import pytest
from dotmap import DotMap
from brownie import ZERO_ADDRESS, Wei, Contract, interface


@pytest.fixture( scope='module', autouse=True )
def someguy(accounts):
    yield accounts[0]


@pytest.fixture( scope='module', autouse=True )
def deployer(accounts):
    yield accounts[1]


@pytest.fixture( scope='module', autouse=True )
def owner(accounts):
    yield accounts[2]


@pytest.fixture( scope='module', autouse=True )
def af(ArrayFactory, owner):
    yield owner.deploy( ArrayFactory )


@pytest.fixture( scope='module', autouse=True )
def apa(ArrayProxyAdmin, owner):
    yield owner.deploy( ArrayProxyAdmin )


@pytest.fixture( scope='module', autouse=True )
def vault(ArrayVault, someguy):
    yield someguy.deploy( ArrayVault )


@pytest.fixture( scope='module', autouse=True )
def vault_two(ArrayVault, someguy):
    yield someguy.deploy( ArrayVault )


@pytest.fixture( scope='module', autouse=True )
def apat(ArrayProxyAdminTimelock, owner, someguy, apa):
    apat = owner.deploy( ArrayProxyAdminTimelock, 6400, [owner], [owner, someguy, ZERO_ADDRESS] )
    apa.transferOwnership( apat.address, {'from': owner} )
    yield apat


@pytest.fixture( scope='module', autouse=True )
def ini(vault, owner):
    data = vault.initialize.encode_input( owner.address )
    yield data


@pytest.fixture( scope='module', autouse=True )
def whale(accounts):
    whale = DotMap()
    whale.dai = accounts.at( '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643', force=True )
    whale.usdc = accounts.at( '0x39aa39c021dfbae8fac545936693ac917d5e7563', force=True )
    whale.wbtc = accounts.at( '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4', force=True )
    whale.renbtc = accounts.at( '0x93054188d876f558f4a66B2EF1d97d16eDf0895B', force=True )
    yield whale
