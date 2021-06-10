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
def factory(developer, ArrayProxyFactory):
    yield ArrayProxyFactory.deploy({'from': developer})


@pytest.fixture(scope='module')
def timelock(governance, developer, user, ArrayTimelock):
    mindelay = 24 * 60 * 60  # one day
    yield ArrayTimelock.deploy(mindelay, [governance], [developer, user], {'from': developer})


@pytest.fixture(scope='module')
def dai(interface):
    yield interface.ERC20('0x6b175474e89094c44da98b954eedeac495271d0f')


@pytest.fixture(scope='module')
def dai_whale(accounts):
    return accounts.at('0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503', force=True)


@pytest.fixture(scope='module')
def proxy_admin(timelock, developer, ArrayProxyAdmin):
    yield ArrayProxyAdmin.deploy(timelock, {'from': developer})


@pytest.fixture(scope='module')
def daomsig(accounts):
    yield accounts.at('0xB60eF661cEdC835836896191EDB87CC025EFd0B7', force=True)


@pytest.fixture(scope='module')
def devmsig(accounts):
    yield accounts.at('0x3c25c256E609f524bf8b35De7a517d5e883Ff81C', force=True)


@pytest.fixture(scope='module')
def mock_proxied(accounts, Mock, factory, MockExtended, developer):
    accounts.default = developer
    m = Mock.deploy()
    txn = factory.deployProxy(m)
    mp = Mock.at(txn.return_value)
    yield mp

# @pytest.fixture(scope='module')
# def roles(factory, developer, governance, timelock, proxy_admin, ArrayRoles):
#     roles_impl = ArrayRoles.deploy({'from': developer})
#     calldata = roles_impl.initialize.encode_input(developer, governance, timelock)
#     transaction = factory.deployProxy(proxy_admin, roles_impl, calldata)
#     return ArrayRoles.at(transaction.return_value)
