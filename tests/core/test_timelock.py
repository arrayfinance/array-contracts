import pytest
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


def test_change_strategy(timelock, vault, storage, roles, dai, strat, developer, governance, second_strat):
    vault.initialize(roles, dai, strat, 997, 1000, {'from': developer})
    old = vault.strategy()
    calldata = vault.setStrategy.encode_input(second_strat)
    delay = 48 * 60 * 60
    timelock.schedule(vault, 0, calldata, 0, 0, delay, {'from': governance})
    chain.sleep(delay + 10)
    timelock.execute(vault, 0, calldata, 0, 0, {'from': developer})
    print(f'{old} != {vault.strategy()}')
    assert vault.strategy() is not old
