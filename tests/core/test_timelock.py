import pytest
import brownie
from brownie import chain
from rich.console import Console

console = Console()


@pytest.fixture(scope='module', autouse=True)
def vault(developer, ArrayVault):
    yield ArrayVault.deploy({'from': developer})


@pytest.fixture(scope='module', autouse=True)
def second_strat(developer, vault, dai, roles, NoopStrategy):
    yield NoopStrategy.deploy(dai, vault, roles, {'from': developer})


@pytest.fixture(scope='module', autouse=True)
def strat(developer, vault, dai, roles, NoopStrategy):
    yield NoopStrategy.deploy(dai, vault, roles, {'from': developer})


@pytest.fixture(scope='module', autouse=True)
def storage(ArrayRolesStorage, developer):
    yield ArrayRolesStorage.deploy({'from': developer})


def test_vault_change_strategy(timelock, vault, storage, roles, dai, strat, developer, governance, second_strat):
    vault.initialize(roles, dai, strat, 997, 1000, {'from': developer})
    old = vault.strategy()
    calldata = vault.setStrategy.encode_input(second_strat)
    delay = 48 * 60 * 60
    timelock.schedule(vault, 0, calldata, 0, 0, delay, {'from': governance})
    chain.sleep(delay + 10)
    timelock.execute(vault, 0, calldata, 0, 0, {'from': developer})
    assert vault.strategy() is not old


# deploys a proxy with mock implementation (one single public address variable 'something'
# proxy is owned by proxyadmin which in turn is owned by timelock, thus the only way to change
# the implementation of the proxy is via the timelock contract
# also shows how the proxy holds storage
def test_upgrade_proxy(rogue, Mock, governance, developer, proxy_admin, factory, timelock):

    # create the implementation, initialization code and deploy the transparent proxy
    vault_logic = Mock.deploy({'from': governance})
    calldata = vault_logic.initialize.encode_input(rogue)
    tx = factory.deployProxy(proxy_admin, vault_logic, calldata)
    vault_proxy = Mock.at(tx.return_value)

    # check that the initialized variable is set
    assert vault_proxy.something() == rogue

    # proxyadmin checks the proxy for implementation
    assert proxy_admin.getProxyImplementation(vault_proxy) == vault_logic

    # proxyadmin chekcs the proxy for admin
    assert proxy_admin.getProxyAdmin(vault_proxy) == proxy_admin
    other_vault_logic = Mock.deploy({'from': governance})

    # calldata = other_vault_logic.initialize.encode_input(rogue)

    # this shouldn't work since the owner of the proxy admin is the timelock!!
    with brownie.reverts():
        proxy_admin.upgrade(vault_proxy, other_vault_logic)

    assert proxy_admin.owner() == timelock

    # now use the timelock to change the proxys implementation
    logic_calldata = other_vault_logic.initialize.encode_input(governance)
    new_proxy_calldata = proxy_admin.upgradeAndCall.encode_input(vault_proxy, other_vault_logic, logic_calldata)
    delay = 48 * 60 * 60
    timelock.schedule(proxy_admin, 0, new_proxy_calldata, 0, 0, delay, {'from': governance})
    chain.sleep(delay + 10)
    timelock.execute(proxy_admin, 0, new_proxy_calldata, 0, 0, {'from': developer})

    assert proxy_admin.getProxyImplementation(vault_proxy) == other_vault_logic

    # since we didn't change the prxoy which holds the storage, this variable should still point to
    # what we had initialized the logic contract previously!!!
    # assert vault_proxy.something() == rogue

    # now let's initialize it again, overwriting the variable
    # other_call_data = vault_proxy.initialize.encode_input(governance, {'from': developer})

    # make sure it's updated
    assert vault_proxy.something() == governance
