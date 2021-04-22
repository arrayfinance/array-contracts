import pytest


@pytest.fixture(scope='module')
def governance(accounts):
    yield accounts[0]


@pytest.fixture(scope='module')
def rogue(accounts):
    yield accounts[1]


@pytest.fixture(scope='module')
def user(accounts):
    yield accounts[2]
