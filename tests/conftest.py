import pytest
from brownie import ZERO_ADDRESS


@pytest.fixture
def owner(accounts):
    yield accounts[0]


@pytest.fixture
def deployer(accounts):
    yield accounts[1]


@pytest.fixture
def someguy(accounts):
    yield accounts[2]


@pytest.fixture
def af(ArrayFactory, owner):
    yield owner.deploy( ArrayFactory )


@pytest.fixture
def apa(ArrayProxyAdmin, owner):
    yield owner.deploy( ArrayProxyAdmin )


@pytest.fixture
def vault(ArrayVault, someguy):
    yield someguy.deploy( ArrayVault )


@pytest.fixture
def vault_two(ArrayVault, someguy):
    yield someguy.deploy( ArrayVault )


@pytest.fixture
def apat(ArrayProxyAdminTimelock, owner, someguy, apa):
    apat = owner.deploy( ArrayProxyAdminTimelock, 6400, [owner], [owner, someguy, ZERO_ADDRESS] )
    apa.transferOwnership( apat.address, {'from': owner} )
    yield apat


@pytest.fixture
def ini(vault, owner):
    data = vault.initialize.encode_input( owner.address )
    yield data


@pytest.fixture
def bancor(BancorFormula, owner):
    bancor = owner.deploy( BancorFormula )
    yield bancor
