import pytest
import brownie
from brownie import ZERO_ADDRESS


@pytest.fixture(autouse=True)
def token(governance, ArrayToken):
    yield ArrayToken.deploy('Array Finance', 'ARRAY', {'from': governance})


def test_roles(token, governance, user, rogue):
    admin = token.DEFAULT_ADMIN_ROLE()
    minter = token.MINTER_ROLE()
    burner = token.BURNER_ROLE()
    assert token.hasRole(admin, governance)
    assert not token.hasRole(admin, rogue)
    assert token.hasRole(minter, ZERO_ADDRESS)
    assert token.hasRole(burner, ZERO_ADDRESS)
    token.grantRole(minter, user, {'from': governance})
    token.grantRole(burner, user, {'from': governance})
    assert token.hasRole(minter, user)
    assert token.hasRole(burner, user)


def test_mint_burn(token, governance, rogue, user):
    minter = token.MINTER_ROLE()
    burner = token.BURNER_ROLE()
    to = user
    amount = 10e18
    assert not token.hasRole(minter, user)
    assert not token.hasRole(burner, user)
    with brownie.reverts():
        token.mint(to, amount, {'from': rogue})
    with brownie.reverts():
        token.burn(to, amount, {'from': rogue})
