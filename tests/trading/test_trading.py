import brownie
from dotmap import DotMap
from hypothesis import Verbosity
from rich.console import Console
from brownie.test import strategy, given
import pytest

console = Console()


@pytest.fixture( scope='module', autouse=True )
def curve(tokens, deployer):
    from scripts.setup import get_curve
    crv = get_curve()
    for t in tokens.values():
        t.approve( crv.address, 2 ** 256 - 1, {'from': deployer} )
    yield crv


@pytest.fixture( scope='module', autouse=True )
def bpt(curve, interface):
    yield interface.ERC20( curve.BP() )


@pytest.fixture( scope='module', autouse=True )
def array(curve, interface):
    yield interface.ERC20( curve.ARRAY() )


@pytest.fixture( scope='module', autouse=True )
def user(deployer, tokens, whales):
    for k, v in tokens.items():
        v.transfer( deployer, v.balanceOf( whales[k] ), {'from': whales[k]} )
    yield deployer


class StateMachine:
    value_to_buy = strategy( 'uint256', min_value=100, max_value=10000 )
    value_to_sell = strategy( 'uint256', min_value=1, max_value=100 )

    def __init__(cls, curve, user, tokens, array, bpt):
        cls.coin = tokens['dai']
        cls.curve = curve
        cls.user = user
        cls.dao = curve.DAO_MULTISIG_ADDR()
        cls.dev = curve.DEV_MULTISIG_ADDR()
        cls.bpt = bpt
        cls.array = array  # cls.bpt_token = bpt.totalSupply()  # cls.array = array.totalSupply()

    def setup(self):
        console.log( f'[yellow] resetting chain..' )

    def rule_buy(self, value_to_buy):

        buy = value_to_buy * 1e18
        balance = self.coin.balanceOf( self.user )
        supply = self.curve.virtualSupply()
        max_supply = self.curve.MAX_ARRAY_SUPPLY()
        mint_full = self.curve.calculateFullArrayTokensGivenERC20Tokens( self.coin.address, buy ) + supply
        mint = self.curve.calculateArrayTokensGivenERC20Tokens( self.coin.address, buy )

        if (balance > buy) and (mint_full < max_supply):
            tx = self.curve.buy( self.coin.address, buy, {'from': self.user} )
            assert mint == tx.return_value
            console.log( f'[green] bought {mint / 1e18:.4f} ARRAY for {value_to_buy} DAI, supply: {supply / 1e18:.2f}' )
        elif mint_full > max_supply:
            with brownie.reverts( "dev: minted array > total supply" ):
                self.curve.buy( self.coin.address, buy, {'from': self.user} )
                console.log( 'minted array > total supply' )
        elif balance < buy:
            with brownie.reverts( "dev: user balance < amount" ):
                console.log( 'buy user balance < amount' )
                self.curve.buy( self.coin.address, buy, {'from': self.user} )

    def rule_sell(self, value_to_sell):

        sell = value_to_sell * 1e18

        balance = self.array.balanceOf( self.user )
        supply = self.curve.virtualSupply()

        if balance >= sell:
            tx = self.curve.sell['uint256']( sell, {'from': self.user} )
            console.log( f'[red] sold {value_to_sell} ARRAY for {tx.return_value / 1e18:.4f} LP, supply: {supply / 1e18:.2f}' )
        else:
            with brownie.reverts( "dev: user balance < amount" ):
                self.curve.sell['uint256']( sell, {'from': self.user} )
                console.log( 'user balance < amount' )

    def invariant(self):

        collateral = self.curve.virtualBalance() / 1e18
        supply = self.curve.virtualSupply() / 1e18
        cw = self.curve.reserveRatio() / 1000000
        price = collateral / (supply * cw)
        m = collateral / (cw * supply ** (1 / cw))
        m = m * 1e6
        console.log( f'slope = {m:.14f}, supply = {supply:.2f}, price = {price:.2f}' )  # m = round( m * 1e6 )
        assert round( m ) == 1


def test_stateful(state_machine, curve, user, tokens, array, bpt):
    console.clear( home=True )
    console.log( '\n Starting..' )
    settings = {"stateful_step_count": 100, "max_examples": 5}
    state_machine( StateMachine, curve, user, tokens, array, bpt, settings=settings )
