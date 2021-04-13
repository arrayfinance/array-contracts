from dotmap import DotMap
from rich.console import Console
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from rich.progress import Progress
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot():
    df = pd.read_csv('../../plot/data.csv')
    # plt.figure()
    df.plot(x='supply', y='price')
    sns.set_theme(style="whitegrid")
    sns.lineplot(x=df.supply, y=df.price, palette="tab9", linewidth=0.5, markers=True)
    plt.show()


class Deployer:
    from brownie.network import rpc, accounts, history, transaction
    from brownie import project, network, ZERO_ADDRESS
    project.load(name='ArrayContractsProject')
    from brownie.project.ArrayContractsProject import interface, ArrayToken, BancorFormula, Curve

    POOL_VALUE = 700_000

    def __init__(self):
        # self.network.disconnect(kill_rpc=True)

        if not self.network.is_connected():
            self.network.connect('mainnet-fork', launch_rpc=True)

        self.whales = DotMap({
            'dai': self.accounts.at('0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503', force=True),
            'usdc': self.accounts.at('0x39aa39c021dfbae8fac545936693ac917d5e7563', force=True),
            'wbtc': self.accounts.at('0xc11b1268c1a384e55c48c2391d8d480264a3a7f4', force=True),
            'renbtc': self.accounts.at('0x93054188d876f558f4a66B2EF1d97d16eDf0895B', force=True),
            'weth': self.accounts.at('0xEab23c1E3776fAd145e2E3dc56bcf739f6e0a393', force=True)})

        self.tokens = DotMap({
            'dai': self.interface.ERC20('0x6b175474e89094c44da98b954eedeac495271d0f'),
            'usdc': self.interface.ERC20('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'),
            'wbtc': self.interface.ERC20('0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'),
            'renbtc': self.interface.ERC20('0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D'),
            'weth': self.interface.weth9('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
        })

        self.uniswap_pairs = DotMap({
            'dai': self.interface.pair('0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11'),
            'usdc': self.interface.pair('0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'),
            'wbtc': self.interface.pair('0xBb2b8038a1640196FbE3e38816F3e67Cba72D940'),
            'renbtc': self.interface.pair('0x81fbef4704776cc5bba0a5df3a90056d2c6900b3')
        })

        self.eth_prices = DotMap({
            'dai': None,
            'usdc': None,
            'wbtc': None,
            'renbtc': None,
            'weth': None
        })

        self.dai_prices = DotMap({
            'dai': None,
            'usdc': None,
            'wbtc': None,
            'renbtc': None,
            'weth': None
        })

        self.decimals = DotMap({
            'dai': None,
            'usdc': None,
            'wbtc': None,
            'renbtc': None,
            'weth': None
        })

        self.weights = DotMap(
            {
                'dai': 0.17, 'usdc': 0.17, 'wbtc': 0.165, 'renbtc': 0.165, 'weth': 0.33
            })

        self.in_balances = DotMap(
            {
                'dai': None,
                'usdc': None,
                'wbtc': None,
                'renbtc': None,
                'weth': None
            }
        )

        self.me = self.accounts[9]
        self.accounts.default = self.me

        self.balance = 411513 * 1e18
        self.cw = 384615

        for k, v in self.tokens.items():
            w = self.whales[k]
            b = v.balanceOf(w)
            v.transfer(self.me, b, {'from': w})

        for acc in self.accounts[:9]:
            acc.transfer(self.me, acc.balance())

        for k in self.decimals.keys():
            self.decimals[k] = self.tokens[k].decimals()

        for p in self.eth_prices.keys():
            self.eth_prices[p] = self._get_prices_in_eth(p) * 10 ** self.decimals[p]

        for p in self.dai_prices.keys():
            self.dai_prices[p] = self._get_prices_in_token('dai', p)

        for k in self.tokens.keys():
            self.in_balances[k] = self.weights[k] * (10 ** self.decimals[k]) * (self.POOL_VALUE / self.dai_prices[k])

    def _get_prices_in_eth(self, symbol):
        if symbol == 'weth':
            return 1

        dec = self.tokens[symbol].decimals()
        pair = self.uniswap_pairs[symbol]
        weth = self.tokens['weth'].address
        r = pair.getReserves()

        eth_price = 0

        if pair.token0() == weth:
            p0 = r[0] / 1e18
            p1 = r[1] / (10 ** dec)
            eth_price = p1 / p0
        elif pair.token1() == weth:
            p0 = r[0] / (10 ** dec)
            p1 = r[1] / 1e18
            eth_price = p0 / p1

        return eth_price

    def _get_prices_in_token(self, t1, t2):
        return self._get_prices_in_eth(t1) / self._get_prices_in_eth(t2)

    def setup_curve(self):
        self.deploy_array_token()
        self.deploy_bancor_formula()
        self.deploy_pool()
        self.deploy_bpool()
        self.deploy_curve()

    def deploy_array_token(self):
        self.accounts.default = self.me
        self.array = self.ArrayToken.deploy('ArrayToken', 'ARRAY', self.ZERO_ADDRESS)

    def deploy_bancor_formula(self):
        self.accounts.default = self.me
        self.bancor = self.BancorFormula.deploy()

    def deploy_pool(self):
        pool_params = ['ARRAYLP', 'Array LP', [self.tokens[k].address for k in self.tokens], [self.in_balances[k] for k in self.tokens],
                       [k * 1e19 for k in self.weights.values()], 1e14]

        pool_rights = [True, True, True, True, False, True]

        crpfact = self.interface.fact('0xed52D8E202401645eDAD1c0AA21e872498ce47D0')
        tx = crpfact.newCrp('0x9424B1412450D0f8Fc2255FAf6046b98213B76Bd', pool_params, pool_rights)
        tx.wait(required_confs=1)
        spool = self.interface.pool(tx.return_value)
        tx.wait(required_confs=1)

        for k in self.tokens.keys():
            self.tokens[k].approve(spool.address, 2 ** 256 - 1)

        spool.createPool(self.balance)
        spool.setCap(2 ** 256 - 1)

        self.pool = spool

    def deploy_bpool(self):
        self.bpool = self.interface.bpool(self.pool.bPool())

    def deploy_curve(self):
        self.accounts.default = self.me
        self.crv = self.Curve.deploy(self.me, self.me, self.array,
                                     self.bancor, self.pool, self.bpool, self.cw)
        self.pool.approve(self.crv, self.balance)
        self.array.grantRole(self.array.MINTER_ROLE(), self.crv)
        self.array.grantRole(self.array.BURNER_ROLE(), self.crv)
        self.crv.initialize(self.balance)
        self.cw = self.crv.reserveRatio() / 1e6
        self.m = self.get_crv_m()
        for v in self.tokens.values():
            v.approve(self.crv, 2 ** 256 - 1)
        for v in self.tokens.values():
            self.crv.addTokenToVirtualLP(v)

    def get_crv_supply(self):
        return self.crv.virtualSupply()

    def get_crv_balance(self):
        return self.crv.virtualBalance()

    def get_crv_m(self):
        return float(self.get_crv_balance()) / (self.cw * float(self.get_crv_supply()) ** (1 / self.cw))

    def plot_curve(self):
        with open("../../plot/data.csv", "wt") as report_file:
            console = Console(file=report_file)
            console.clear(home=True)
            self.accounts.default = self.me
            console.print('supply,price')
            l = []
            with Progress(transient=True) as progress:
                while not self.get_crv_supply() > 100000e18:
                    progress.start()
                    for k, v in self.tokens.items():
                        dec = v.decimals()

                        buy = 50000 * 10 ** dec / self.dai_prices[k]

                        if v.balanceOf(self.me) <= buy:
                            print(f'{k} has not enough balance\n')
                        elif buy >= self.bpool.getBalance(v.address) / 2 - 100:
                            print(f'{k} if over max in\n')
                        else:
                            print(f'{k} buying\n')

                        tx = self.crv.buy(v.address, int(buy))

                        if tx.return_value:
                            purchase = tx.return_value / 1e18
                            buy_amount_in_dai = (buy / 10 ** dec) * self.dai_prices[k]
                            sp = self.get_crv_supply() / 1e18
                            price_in_dai = buy_amount_in_dai / purchase
                            if k == 'dai':
                                console.print(f'{sp:.2f},{price_in_dai:.2f}')
                                l.append({'supply': int(sp), 'price': float(price_in_dai)})

    def calc_collateral(self, m, n):
        cw = 1 / (1 + n)
        self.balance = self.m * (self.cw * float(self.get_crv_supply()) ** (1 / self.cw))

    def pool_in(self, factor):
        m = 2 ** 256 - 1
        self.pool.joinPool(factor, [m, m, m, m, m])

    def pool_out(self, factor):
        m = 0
        self.pool.exitPool(factor, [m, m, m, m, m])


d = Deployer()
d.setup_curve()
d.plot_curve()
