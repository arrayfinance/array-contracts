import pytest
from brownie import ZERO_ADDRESS, Wei, Contract


@pytest.fixture(scope='module', autouse=True)
def owner(accounts):
    yield accounts[0]


@pytest.fixture(scope='module', autouse=True)
def deployer(accounts):
    yield accounts[1]


@pytest.fixture(scope='module', autouse=True)
def someguy(accounts):
    yield accounts[2]


@pytest.fixture(scope='module', autouse=True)
def af(ArrayFactory, owner):
    yield owner.deploy( ArrayFactory )


@pytest.fixture(scope='module', autouse=True)
def apa(ArrayProxyAdmin, owner):
    yield owner.deploy( ArrayProxyAdmin )


@pytest.fixture(scope='module', autouse=True)
def vault(ArrayVault, someguy):
    yield someguy.deploy( ArrayVault )


@pytest.fixture(scope='module', autouse=True)
def vault_two(ArrayVault, someguy):
    yield someguy.deploy( ArrayVault )


@pytest.fixture(scope='module', autouse=True)
def apat(ArrayProxyAdminTimelock, owner, someguy, apa):
    apat = owner.deploy( ArrayProxyAdminTimelock, 6400, [owner], [owner, someguy, ZERO_ADDRESS] )
    apa.transferOwnership( apat.address, {'from': owner} )
    yield apat


@pytest.fixture(scope='module', autouse=True)
def ini(vault, owner):
    data = vault.initialize.encode_input( owner.address )
    yield data


