from dotmap import DotMap
from rich.console import Console
import time
import os
from sigfig import round
from dotenv import load_dotenv


def unlock_account(address: str) -> None:
    web3.provider.make_request("hardhat_impersonateAccount", [address])


class Deployer:
    from brownie import interface, ArrayToken, BancorFormula, Curve, accounts, ArrayToken, BancorFormula, Curve, interface, ZERO_ADDRESS, chain, web3

    POOL_VALUE = 700_000

    accounts_to_unlock = ['0x5d3a536e4d6dbd6114cc1ead35777bab948e3643',
                          '0x39aa39c021dfbae8fac545936693ac917d5e7563',
                          '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4',
                          '0x93054188d876f558f4a66B2EF1d97d16eDf0895B',
                          '0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503',
                          '0x13aec50f5D3c011cd3fed44e2a30C515Bd8a5a06',
                          '0x16463c0fdB6BA9618909F5b120ea1581618C1b9E']

    def __init__(self, n=1.6):

        for a in self.accounts_to_unlock:
            self.web3.provider.make_request("hardhat_impersonateAccount", [a])

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

        self.calc_collateral(n)

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

    def setup(self):
        self._deploy_array_token()
        self._deploy_bancor_formula()
        self._deploy_pool()
        self._deploy_bpool()

    def _deploy_array_token(self):
        self.accounts.default = self.me
        self.array = self.ArrayToken.deploy('ArrayToken', 'ARRAY', self.ZERO_ADDRESS)

    def _deploy_bancor_formula(self):
        self.accounts.default = self.me
        self.bancor = self.BancorFormula.deploy()

    def _deploy_pool(self):
        pool_params = ['ARRAYLP', 'Array LP', [self.tokens[k] for k in self.tokens], [self.in_balances[k] for k in self.tokens],
                       [self.weights[k] * 1e19 for k in self.weights], 1e14]

        pool_rights = [True, True, True, True, False, True]

        crpfact = self.interface.fact('0xed52D8E202401645eDAD1c0AA21e872498ce47D0')
        tx = crpfact.newCrp('0x9424B1412450D0f8Fc2255FAf6046b98213B76Bd', pool_params, pool_rights)
        spool = self.interface.pool(tx.events[1]['pool'])

        for k in self.tokens:
            self.tokens[k].approve(spool.address, 2 ** 256 - 1)

        spool.createPool(self.balance)
        spool.setCap(2 ** 256 - 1)

        self.pool = spool

    def _deploy_bpool(self):
        self.bpool = self.interface.bpool(self.pool.bPool())

    def deploy_curve(self):
        self.balance = self.balance
        self.accounts.default = self.me
        self.crv = self.Curve.deploy(self.me, self.me, self.array,
                                     self.bancor, self.pool, self.bpool, self.cw)

        self.pool.approve(self.crv, self.balance)
        self.array.grantRole(self.array.MINTER_ROLE(), self.crv)
        self.array.grantRole(self.array.BURNER_ROLE(), self.crv)

        self.crv.initialize(self.balance)
        for k in self.tokens:
            self.tokens[k].approve(self.crv, 2 ** 256 - 1)
        for k in self.tokens:
            self.crv.addTokenToVirtualLP(self.tokens[k])

    def get_crv_supply(self):
        return self.crv.virtualSupply()

    def get_crv_balance(self):
        return self.crv.virtualBalance()

    def get_crv_m(self):
        cw = self.cw / 1e6
        balance = self.get_crv_balance() / 1e18
        supply = self.get_crv_supply() / 1e18
        return balance / (cw * (supply ** (1 / cw)))

    def get_crv_n(self):
        cw = self.cw / 1e6
        return (1 / cw) - 1

    def get_price_at(self, at):
        m = self.get_crv_m()
        n = self.get_crv_n()
        return m * at ** n

    def get_curve_data(self):
        konsole = Console()
        start_time = int(time.time())
        counter = 0
        with open("data.csv", "wt") as report_file:
            console = Console(file=report_file)
            console.print('supply,price')

            konsole.clear(home=True)
            l = []

            tokens_ = self.tokens
            while counter < 21:
                for k in tokens_:
                    v = tokens_[k]
                    print(v)
                    print(tokens_)
                    dec = v.decimals()

                    buy = 50000 * 10 ** dec / self.dai_prices[k]
                    t = (int(time.time()) - start_time) / 60

                    if v.balanceOf(self.me) <= buy or buy >= self.bpool.getBalance(v.address) / 2 - 100:
                        tokens_.pop(k)
                        continue
                    tx = self.crv.buy(v.address, int(buy))

                    if tx.return_value:
                        purchase = tx.return_value / 1e18
                        buy_amount_in_dai = (buy / 10 ** dec) * self.dai_prices[k]
                        sp = self.get_crv_supply() / 1e18
                        price_in_dai = buy_amount_in_dai / purchase
                        if k == 'dai':
                            counter = counter + 1;
                            konsole_supply = int(self.get_crv_supply() / 1e18)
                            konsole.rule(title=f'[red]{t:.2f} minutes, [blue] supply = {konsole_supply}, [yellow] price = {price_in_dai}')
                            console.print(f'{sp:.2f},{price_in_dai:.2f}')
                            l.append({'supply': int(sp), 'price': float(price_in_dai)})

    def calc_collateral(self, n):
        n = float(n)
        cw = 1 / (1 + n)
        m = 100 / (10000 ** n)
        balance = m * (cw * float(10000) ** (1 / cw))
        balance = balance

        self.balance = 3.437 * balance * 1e18
        self.cw = int(round(cw * 1e6, 6))

    def pool_in(self, factor):
        m = 2 ** 256 - 1
        self.pool.joinPool(factor, [m, m, m, m, m])

    def pool_out(self, factor):
        m = 0
        self.pool.exitPool(factor, [m, m, m, m, m])


def main():
    load_dotenv()
    n = os.getenv('EXPONENT')
    d = Deployer(float(n))
    d.setup()
    d.deploy_curve()
    d.get_curve_data()

    print(f'm = {d.get_crv_m()})')
    print(f'n = {d.get_crv_n()}')
