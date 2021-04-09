import pytest
from dotmap import DotMap


@pytest.fixture( scope="module", autouse=True )
def deployer(accounts):
    yield accounts[0]


@pytest.fixture( scope='module', autouse=True )
def someguy(accounts):
    yield accounts[1]


@pytest.fixture( scope='module', autouse=True )
def tokens():
    from scripts.tokens import tokens
    yield tokens


@pytest.fixture( scope='module', autouse=True )
def whales():
    from scripts.whales import whales
    yield whales
