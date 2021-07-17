import pytest
from dotmap import DotMap
import pandas as pd
import matplotlib.pyplot as plt


@pytest.fixture(scope='module')
def spool(interface, daomsig):
    spool = interface.pool(
        '0xA800cDa5f3416A6Fb64eF93D84D6298a685D190d')
    spool.setCap(2 ** 256 - 1, {'from': daomsig})
    yield spool


@pytest.fixture(scope='module')
def bpool(interface):
    yield interface.bpool(
        '0x02e1300A7E6c3211c65317176Cf1795f9bb1DaAb')


@pytest.fixture(scope='module')
def af(ArrayFinance, spool, roles, daomsig, developer):
    af = ArrayFinance.deploy(roles, {'from': developer})
    spool.approve(af, 2 ** 256 - 1, {'from': daomsig})
    af.initialize({'from': daomsig})
    yield af


@pytest.fixture(scope='function')
def tokens(bpool, spool, daomsig, developer, rich, dai, usdc, weth, wbtc, renbtc):
    tokens = DotMap()
    tokens.dai.contract = dai
    tokens.usdc.contract = usdc
    tokens.weth.contract = weth
    tokens.wbtc.contract = wbtc
    tokens.renbtc.contract = renbtc
    yield tokens


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.mark.skip()
def test_stateful(af, spool, bpool, accounts, daomsig, developer, rich, tokens):
    accounts.default = rich
    for k, v in tokens.items():
        v.contract.approve(af, 2 ** 256 - 1, {'from': rich})

    l = []
    while af.totalSupply() < 100000e18:
        for k, v in tokens.items():
            if k != 'dai':
                dec = v.contract.decimals()
                amount = bpool.getBalance(v.contract) / 3
                af.buy(v.contract, amount, 5, {'from': rich})
            elif k == 'dai':
                amount = bpool.getBalance(v.contract) / 3
                tx = af.buy(v.contract, amount, 5, {'from': rich})
                price = amount / tx.return_value
                l.append({'supply': af.totalSupply() / 1e18, 'price': price})
                print(f'{af.totalSupply() / 1e18:.4f} -> {price:.4f} DAI')
        if af.totalSupply() > 90000e18:
            break

    df = pd.DataFrame(l)
    df.to_csv('data.csv')
