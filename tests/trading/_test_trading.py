import brownie
from brownie import history
from rich.console import Console
from brownie.test import strategy
from sigfig import round
import pytest
import pandas as pd
import matplotlib.pyplot as plt

PRECISION_EXP = 18
PRECISION = 10 ** PRECISION_EXP
PCT_ARRAY_TO_DAO = 0.05
PCT_TOKEN_TO_DAO = 0.2
PCT_TOKEN_TO_DEV = 0.05

console = Console()


@pytest.fixture(scope='module', autouse=True)
def curve(tokens, deployer):
    from scripts.setup import get_curve
    crv = get_curve()
    for t in tokens.values():
        t.approve(crv.address, 2 ** 256 - 1, {'from': deployer})
    yield crv


@pytest.fixture(scope='module', autouse=True)
def dao(curve):
    yield curve.DAO_MULTISIG_ADDR()


@pytest.fixture(scope='module', autouse=True)
def dev(curve):
    yield curve.DEV_MULTISIG_ADDR()


@pytest.fixture(scope='module', autouse=True)
def crp(curve, interface):
    yield interface.pool(curve.CRP())


@pytest.fixture(scope='module', autouse=True)
def bpt(curve, interface):
    yield interface.bpool(curve.BP())


@pytest.fixture(scope='module', autouse=True)
def array(curve, interface):
    yield interface.ERC20(curve.ARRAY())


@pytest.fixture(scope='module', autouse=True)
def user(deployer, tokens, whales):
    for k, v in tokens.items():
        for w in whales[k]:
            v.transfer(deployer, v.balanceOf(w), {'from': w})
    yield deployer


def assert_equal(first, second):
    # significant figures equal to precision - 2 to account for rounding errors in the range of e2 wei
    assert round(int(first) / PRECISION, sigfigs=PRECISION_EXP - 2) == round(int(second) / PRECISION, sigfigs=PRECISION_EXP - 2)


def equation(curve):
    collateral = curve.virtualBalance() / PRECISION
    supply = curve.virtualSupply() / PRECISION
    cw = curve.reserveRatio() / 1000000
    m = collateral / (cw * supply ** (1 / cw))
    return m, cw


class StateMachine:
    add_supply = strategy('uint256', min_value=0, max_value=1000000000)
    value_to_buy = strategy('uint256', min_value=1, max_value=100000)
    value_to_sell = strategy('uint256', min_value=1, max_value=1000)

    def __init__(cls, curve, user, tokens, array, dao, dev, crp, bpt):
        cls.coin = tokens['dai']
        cls.curve = curve
        cls.user = user
        cls.dao = dao
        cls.dev = dev
        cls.array = array
        cls.crp = crp
        cls.bpt = bpt
        console.clear(home=True)

    def setup(self):
        console.log(f'[yellow] resetting chain..')
        self.trade = None
        self.bought = 0
        self.sold = 0

    def initialize_add_supply(self, add_supply):

        supply = min(add_supply * 1e18, self.coin.balanceOf(self.user) / 2)

        while self.curve.virtualSupply() < self.curve.MAX_ARRAY_SUPPLY():
            max_buy = (self.bpt.getBalance(self.coin) / 2) - 1e18

            if self.curve.virtualSupply() + self.curve.calculateArrayTokensGivenERC20Tokens(self.coin, max_buy) > supply:
                break
            else:
                self.curve.buy(self.coin, max_buy, {'from': self.user})

        console.log(f'[yellow] setting to {(self.curve.virtualSupply()) / 1e18:.2f} ARRAY supply')

    def rule_buy(self, value_to_buy):
        console.log(f'[yellow] trying to buy for {value_to_buy} DAI')
        buy = value_to_buy * PRECISION
        balance = self.coin.balanceOf(self.user)
        supply = self.curve.virtualSupply()
        max_supply = self.curve.MAX_ARRAY_SUPPLY()
        mint = self.curve.calculateArrayTokensGivenERC20Tokens(self.coin.address, buy)

        self.sold = 0
        self.bought = 0

        user_token_init = self.coin.balanceOf(self.user)
        user_array_init = self.array.balanceOf(self.user)
        dao_token_init = self.coin.balanceOf(self.dao)
        dev_token_init = self.coin.balanceOf(self.dev)
        dao_array_init = self.array.balanceOf(self.dao)
        array_supply_init = self.array.totalSupply()

        max_in = self.bpt.getBalance(self.coin) / 2

        # this is the supply that can still be minted, ie the maximum minus the current
        mint_full = max_supply - supply

        minted_to_user = 0

        if mint_full > max_supply:

            console.log('minted array > total supply')
            with brownie.reverts("dev: minted array > total supply"):
                self.curve.buy(self.coin.address, buy, {'from': self.user})

            return

        elif balance < buy:

            console.log('buy user balance < amount')
            with brownie.reverts("dev: user balance < amount"):
                self.curve.buy(self.coin.address, buy, {'from': self.user})

            return

        elif buy > max_in:

            console.log('ratio in to high')
            with brownie.reverts("dev: ratio in to high"):
                self.curve.buy(self.coin.address, buy, {'from': self.user})

            return

        else:

            self.curve.buy(self.coin.address, buy, {'from': self.user})
            tx = history[-1]
            minted_to_user = tx.return_value

            # change values for printout
            self.bought = minted_to_user
            self.buy_cost = buy
            self.trade = 'buy'

            price_in_coin = (self.buy_cost / 1e18) / (self.bought / 1e18)
            transaction = f'[green]bought {self.bought / 1e18:.2f} ARRAY for {self.buy_cost / 1e18:.2f} DAI'
            console.log(f'{transaction}, supply = {supply / 1e18:.2f}, price = {price_in_coin:.4f} DAI / ARRAY')

        total_array_minted = self.array.totalSupply() - array_supply_init

        # check that user received all minted array
        assert_equal(self.array.balanceOf(self.user), user_array_init + minted_to_user)

        # check that user has spent his token
        assert_equal(self.coin.balanceOf(self.user), user_token_init - buy)

        # check that dao has received all token
        token_to_dev = buy * PCT_TOKEN_TO_DEV
        assert_equal(self.coin.balanceOf(self.dev), dev_token_init + token_to_dev)

        # check that dao received all array
        array_to_dao = total_array_minted * PCT_ARRAY_TO_DAO
        assert_equal(self.array.balanceOf(self.dao), dao_array_init + array_to_dao)

        # check that dao received all token
        token_to_dao = buy * PCT_TOKEN_TO_DAO
        assert_equal(self.coin.balanceOf(self.dao), dao_token_init + token_to_dao)

        # check that the total has been added to virtual supply
        assert_equal(self.curve.virtualSupply(), array_supply_init + array_to_dao + mint)

    def rule_sell(self, value_to_sell):
        console.log(f'[yellow] trying to sell for {value_to_sell} ARRAY')
        sell = value_to_sell * PRECISION
        self.bought = 0
        self.sold = 0

        balance = self.array.balanceOf(self.user)
        virtual_balance_init = self.curve.virtualBalance()
        virtual_supply_init = self.curve.virtualSupply()

        user_token_init = self.coin.balanceOf(self.user)
        user_array_init = self.array.balanceOf(self.user)
        dao_token_init = self.coin.balanceOf(self.dao)
        dev_token_init = self.coin.balanceOf(self.dev)
        dao_array_init = self.array.balanceOf(self.dao)
        user_pool_init = self.crp.balanceOf(self.user)
        array_supply_init = self.array.totalSupply()
        pt_supply_init = self.crp.totalSupply()
        supply = self.curve.virtualSupply()

        self.sell_return = 0

        if sell > balance:

            console.log('user balance < amount')
            with brownie.reverts("dev: user balance < amount"):
                self.curve.sell['uint256'](sell, {'from': self.user})

            return

        else:

            self.curve.sell['uint256'](sell, {'from': self.user})
            tx = history[-1]

            self.sold = sell / 1e18
            self.trade = 'sell'
            self.sell_return = tx.return_value / 1e18
            price_in_lp = self.sold / self.sell_return
            transaction = f'[yellow]sold {self.sold:.2f} ARRAY for {self.sell_return:.2f} LP'
            console.log(f'{transaction}, supply = {supply / 1e18:.2f}, price = {price_in_lp:.4f}')

        #  user now should have received pool tokens
        assert_equal(self.crp.balanceOf(self.user), user_pool_init + tx.return_value)

        # check that user lost the burned array
        assert_equal(self.array.balanceOf(self.user), user_array_init - sell)

        # check that virtual balance changed
        assert_equal(self.curve.virtualBalance(), virtual_balance_init - tx.return_value)

        # check that virtual supply changed
        assert_equal(self.curve.virtualSupply(), virtual_supply_init - sell)

        # check that array were burned
        assert_equal(self.array.totalSupply(), array_supply_init - sell)

    def invariant(self):

        # slope of the _curve should not be changed, ie ratio of virtual supply to virtual balance should be
        # as predicted by bancor formula

        coin_symbol = self.coin.symbol()

        assert cw == 0.333333
        assert round(m, 2) == 1


def test_price(curve, user, tokens, interface):
    console.clear(home=True)
    dai = tokens.dai
    l = []
    bpool = interface.bpool(curve.BP())
    while True:
        try:
            maxv = bpool.getBalance(dai)/2 + 1e18
            curve.buy(dai, maxv, {'from': user})
            value = history[-1].return_value
            # price = maxv / (value[1] / 1e18)
            supply = curve.virtualSupply()
            # l.append(d)
            price_dai = maxv / value
            eq = equation(curve)
            m = eq[0]
            cw = eq[1]
            console.log(f'supply : {supply / 1e18}, dai_price: {price_dai:.4f}, m = {m}, cw = {cw}')
            l.append({'supply': int(supply/1e18), 'price': float(price_dai)})
            if supply > 50000e18:
                break
        except Exception:
            break
            # console.log(f'supply: {supply / 1e18},   price: {price:.2f} DAI for one ARRAY')

    df = pd.DataFrame(l)
    plt.figure()
    df.plot(x='supply', y='price')
    plt.show()
# def test_stateful(state_machine, _curve, user, tokens, array, dao, dev, crp, bpt):
#     console.clear(home=True)
#     console.log('\n Starting..')
#     state_machine(StateMachine, _curve, user, tokens, array, dao, dev, crp, bpt)
