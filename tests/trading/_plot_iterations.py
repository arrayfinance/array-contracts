from rich.console import Console
import pytest
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


@pytest.fixture(scope='function', autouse=True)
def deployer():
    from scripts.deployer import Deployer
    d = Deployer()
    d.setup_curve()
    yield d


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# cycles through the balancer pool tokens and adds those until max. array supply
def test_multiple_iterations(deployer, accounts):
    with open("data.csv", "wt") as report_file:
        console = Console(file=report_file)
        console.clear(home=True)
        accounts.default = deployer.me
        console.log('supply', 'price(DAI)')
        l = []
        while deployer.get_crv_supply() <= 100000 * 1e18:
            for k, v in deployer.tokens.items():
                try:
                    dec = v.decimals()
                    buy = min(v.balanceOf(deployer.me), (deployer.bpool.getBalance(v.address) / 2) - 10 ** (dec - 4))
                    tx = deployer.crv.buy(v.address, buy)
                    purchase = tx.return_value / 1e18
                    buy_amount_in_dai = (buy / 10 ** dec) * deployer.dai_prices[k]
                    sp = deployer.get_crv_supply() / 1e18
                    price_in_dai = buy_amount_in_dai / purchase
                    console.log(f'{sp:.2f},{price_in_dai:.2f}')
                    l.append({'supply': int(sp), 'price': float(price_in_dai)})
                except Exception:
                    pass

        df = pd.DataFrame(l)
        df.to_csv('data.csv')
        plt.figure()
        df.plot(x='supply', y='price')
        plt.show()
