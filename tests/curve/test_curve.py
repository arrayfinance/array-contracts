import pytest
import brownie
from brownie import ZERO_ADDRESS


@pytest.fixture( scope='module', autouse=True )
def curve():
    from scripts.setup import curve
    yield curve


def test_revert_already_initialized_curve(curve, accounts):
    initial_lp_tokens = 333_333 * 1e18
    me = accounts[0]
    with brownie.reverts( 'Initializable: contract is already initialized' ):
        curve.initialize( initial_lp_tokens, {'from': me} )


# verifies that the balance and supply is according to mxˆ2 with m = 1e-6
# m = collateral / (CW * tokenSupply ^ (1 / CW))
def test_correct_slope(curve, accounts):
    collateral = curve.virtualBalance() / 1e18
    supply = curve.virtualSupply() / 1e18
    cw = curve.reserveRatio() / 1000000

    m = collateral / (cw * supply ** (1 / cw))
    m = round( m * 1e6 )
    assert m == 1
