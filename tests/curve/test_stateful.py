from brownie.test import strategy
from rich.console import Console

console = Console()


class StateMachine:
    index = strategy('uint', min_value=0, max_value=4)
    value = strategy('uint', min_value=1, max_value=99)

    def __init__(cls, d):
        # initialize curve contract
        cls.d = d
        cls.d.initialize_curve()

    def rule_buy(self, index, value):
        t = list(self.d.tokens.values())[index]
        amount = min(self.d.bpool.getBalance(t.address) * (value / 200), t.balanceOf(self.d.me))
        amount_in_dai = (amount / 10 ** t.decimals()) * list(self.d.dai_prices.values())[index]
        tx = self.d.crv.buy(t.address, int(amount), 2)
        price_in_dai = amount_in_dai / (tx.return_value / 1e18)
        console.log(f'[green]Paid {amount / 10 ** t.decimals():.2f} of {t.symbol()} and received {tx.return_value / 1e18:.2f} ARRAY\n'
                    f'Supply is {self.d.get_crv_supply() / 1e18:.2f}   Price was {price_in_dai:.2f} DAI/ARRAY')

    def rule_sell(self, value):
        amount = self.d.array.balanceOf(self.d.me) * (value / 1000)
        if amount > 0:
            tx = self.d.crv.sell['uint256'](int(amount))
            console.log(f'[red]Sold {amount / 1e18:.2f} ARRAY and received {tx.return_value / 1e18:.2f} LP\n'
                        f'Supply is {self.d.get_crv_supply() / 1e18:.2f}')
        else:
            return


def test_stateful(state_machine):
    from scripts.deployer import Deployer
    d = Deployer()
    d.setup()
    d.deploy_curve()
    state_machine(StateMachine, d)
