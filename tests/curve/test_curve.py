import pytest
import brownie
from brownie import ZERO_ADDRESS


@pytest.fixture( scope='module', autouse=True )
def me(accounts):
    yield accounts[0]


@pytest.fixture( scope='module', autouse=True )
def array_token(ArrayToken, me):
    yield ArrayToken.deploy( 'ArrayToken', 'ARRAY', ZERO_ADDRESS, {'from': me} )


@pytest.fixture( scope='module', autouse=True )
def bancor_formula(BancorFormula, me):
    yield BancorFormula.deploy( {'from': me} )


@pytest.fixture( scope='module', autouse=True )
def smartpool(me):
    from scripts.create_smartpool import main
    yield main()


@pytest.fixture( scope='module', autouse=True )
def curve(Curve, me, array_token, bancor_formula, smartpool):
    yield Curve.deploy( me, array_token, bancor_formula, smartpool, {'from': me} )


def test_initialize_curve(me, smartpool, curve, array_token):
    initial_lp_tokens = smartpool.totalSupply()
    smartpool.approve( curve.address, initial_lp_tokens, {'from': me} )
    array_token.grantRole( array_token.MINTER_ROLE(), curve.address, {'from': me} )
    array_token.grantRole( array_token.BURNER_ROLE(), curve.address, {'from': me} )

    curve.initialize( initial_lp_tokens, {'from': me} )


def test_revert_already_initialized_curve(me, smartpool, curve, array_token):
    initial_lp_tokens = smartpool.totalSupply()
    smartpool.approve( curve.address, initial_lp_tokens, {'from': me} )
    array_token.grantRole( array_token.MINTER_ROLE(), curve.address, {'from': me} )
    array_token.grantRole( array_token.BURNER_ROLE(), curve.address, {'from': me} )

    with brownie.reverts( 'Initializable: contract is already initialized' ):
        curve.initialize( initial_lp_tokens, {'from': me} )
