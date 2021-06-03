import pytest
from brownie import *

@pytest.fixture(scope='module')
def governance(accounts):
    yield accounts[0]


@pytest.fixture(scope='module')
def developer(accounts):
    yield accounts[1]


@pytest.fixture(scope='module')
def user(accounts):
    yield accounts[2]


@pytest.fixture(scope='module')
def evil(accounts):
    yield accounts[3]


@pytest.fixture(scope='module')
def factory(developer, ArrayProxyFactory):
    yield ArrayProxyFactory.deploy({'from': developer})


@pytest.fixture(scope='module')
def mock(Mock, developer):
    yield Mock.deploy({'from': developer})


@pytest.fixture(scope='module')
def timelock(governance, developer, user, ArrayTimelock):
    mindelay = 24 * 60 * 60  # one day
    yield ArrayTimelock.deploy(mindelay, [governance], [developer, user], {'from': developer})


@pytest.fixture(scope='module')
def proxy_admin(timelock, developer, ArrayProxyAdmin):
    yield ArrayProxyAdmin.deploy(timelock, {'from': developer})


@pytest.fixture(scope='module')
def roles(factory, developer, governance, timelock, proxy_admin, ArrayRoles):
    roles_impl = ArrayRoles.deploy({'from': developer})
    calldata = roles_impl.initialize.encode_input(developer, governance, timelock)
    transaction = factory.deployProxy(proxy_admin, roles_impl, calldata)
    return ArrayRoles.at(transaction.return_value)
