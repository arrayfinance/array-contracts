import pytest
from brownie.test import strategy
from rich.console import Console
import numpy as np
import time

console = Console()

# higher precision might cause assertions to fail
PRECISION = 6


@pytest.fixture(scope='module', autouse=True)
def vault(developer, ArrayVault):
    yield ArrayVault.deploy({'from': developer})


@pytest.fixture(scope='module', autouse=True)
def strat(developer, vault, dai, roles, NoopStrategy):
    yield NoopStrategy.deploy(dai, vault, roles, {'from': developer})


class StateMachine:
    deposit = strategy('uint256', min_value='5000 ether', max_value='100000 ether')
    reward = strategy('uint256', min_value=1, max_value=10)

    def __init__(cls, vault, roles, dai, strat, user, developer, dai_whale):
        vault.initialize(roles, dai, strat, 997, 1000, {'from': developer})
        dai.transfer(user, dai.balanceOf(dai_whale), {'from': dai_whale})
        dai.approve(vault, 2 ** 256 - 1, {'from': user})

        cls.vault = vault
        cls.user = user
        cls.developer = developer
        cls.strat = strat
        cls.dai_whale = dai_whale
        cls.dai = dai

    def setup(self):
        self.ppfs = int(self.vault.getPricePerFullShare())

    def rule_deposit(self, deposit):

        if deposit == 0:
            return

        # the strategy seems to be biased towards the minimum so this is creating some additional variance
        rng = np.random.default_rng()
        deposit = rng.random() * deposit

        # so that we can compare the values afterwards
        user_balance_before = self.vault.underlyingBalanceWithInvestmentForHolder(self.user)
        total_supply_before = self.vault.totalSupply()
        vault_balance_before = self.vault.underlyingBalanceInVault()

        # this must be here, before the deposit
        shares_issued = deposit / (self.vault.getPricePerFullShare() / 1e18)

        console.rule(
            f'[green]Deposit of [bold]${deposit / 1e18:,.2f} Dai -- [blue]{shares_issued / 1e18:.2f} vault shares')

        self.vault.deposit(deposit, {'from': self.user})

        # underlying balance in vault + strategy should be increased by deposit(underlying)
        assert round(self.vault.underlyingBalanceWithInvestmentForHolder(self.user) / 1e18, PRECISION) == round(
            (user_balance_before + deposit) / 1e18,
            PRECISION)

        # total supply (total shares) should increase by the number of shares that were minted
        assert round(self.vault.totalSupply() / 1e18, PRECISION) == round((total_supply_before + shares_issued) / 1e18,
                                                                          PRECISION)

        # vault balance should increase by the depopsit amount (underlying)
        assert round(self.vault.underlyingBalanceInVault() / 1e18, PRECISION) == round(
            (vault_balance_before + deposit) / 1e18,
            PRECISION)

    def rule_invest(self, reward):
        if reward == 0:
            return

        before = self.vault.underlyingBalanceWithInvestment()

        # here we get a random % of the vault+strategy's balance
        rng = np.random.default_rng()
        reward = rng.random() * reward / 2
        stuff = (reward / 100) * before

        if stuff == 0:
            return

        console.rule(f'[red] Strategy return: ${stuff / 1e18:.2f} DAI', style='blue')

        # and invest it in the strategy
        self.vault.doStuff({'from': self.developer})

        # since the strategy at this point doesn't do anything though, we have to manually give it additional funds
        # thus 'simulating' the returns
        self.dai.transfer(self.strat, stuff, {'from': self.user})
        assert round((before + stuff) / 1e18, PRECISION) == round(self.vault.underlyingBalanceWithInvestment() / 1e18,
                                                                  PRECISION)

    def rule_withdraw(self):
        if self.vault.underlyingBalanceWithInvestment() == 0:
            return

        vault_balance_before = self.vault.underlyingBalanceWithInvestment()
        total_supply_before = self.vault.totalSupply()

        # underlying balance of user before withdrawal
        before = self.dai.balanceOf(self.user)

        # we get a random % of his shares in the vault
        rng = np.random.default_rng()
        wd = self.vault.balanceOf(self.user) * rng.random()

        # withdraw them, burning shares and transfering him underlying
        self.vault.withdraw(wd, {'from': self.user})

        # this is the underlying that he receives
        wd_dai = self.dai.balanceOf(self.user) - before

        # the vault+strategy should have lost exactly the amount of underlying that user receivved
        assert self.vault.underlyingBalanceWithInvestment() == vault_balance_before - wd_dai

        # wd are the shares that were burned and should reduce the total supply in the vault
        assert self.vault.totalSupply() == total_supply_before - wd

        console.rule(f'[yellow] Withdrawing: ${wd / 1e18:.2f} shares, ${wd_dai / 1e18:,.2f} DAI', style='magenta')

    def invariant(self):
        if self.vault.totalSupply() > 0:

            # ppfs should never go down
            assert self.vault.getPricePerFullShare() >= self.ppfs
            self.ppfs = self.vault.getPricePerFullShare()
            console.rule(f'[bold] PPFS: {round(self.ppfs / 1e18, PRECISION):.6f}', style='red')

            # invariant - ppfs is always equal to balance divided by totalSupply
            assert round(self.ppfs / 1e18, PRECISION) == round(
                self.vault.underlyingBalanceWithInvestment() / self.vault.totalSupply(), PRECISION)
        else:
            pass


def test_stateful(vault, roles, dai, strat, user, developer, dai_whale, state_machine):
    state_machine(StateMachine, vault, roles, dai, strat, user, developer, dai_whale)
