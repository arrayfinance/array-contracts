import pytest
import brownie
from brownie import ZERO_ADDRESS


@pytest.fixture(scope='function', autouse=True)
def deployer():
    from scripts.deployer import Deployer
    d = Deployer()
    d.setup_curve()
    yield d


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_revert_already_initialized_curve(deployer, accounts, isolation):
    initial_lp_tokens = 333_333 * 1e18
    accounts.default = deployer.me
    with brownie.reverts('Initializable: contract is already initialized'):
        deployer.crv.initialize(initial_lp_tokens)


# verifies that the balance and supply is according to mxˆ2 with m = 1e-6
# m = collateral / (CW * tokenSupply ^ (1 / CW))
def test_correct_slope(deployer, isolation):
    collateral = deployer.get_crv_balance() / 1e18
    supply = deployer.get_crv_supply() / 1e18
    cw = deployer.crv.reserveRatio() / 1000000

    m = collateral / (cw * supply ** (1 / cw))
    m = round(m * 1e6)
    assert m == 1


# add, check for, and remove tokens to the virtual registry which inherits from oz's
# enumerable set
def test_add_remove_virtual_lp(deployer, accounts, isolation):
    accounts.default = deployer.me
    dai = deployer.tokens.dai
    weth = deployer.tokens.weth
    wbtc = deployer.tokens.wbtc

    assert deployer.crv.isTokenInVirtualLP(dai.address)
    assert deployer.crv.isTokenInVirtualLP(weth.address)
    assert deployer.crv.isTokenInVirtualLP(wbtc.address)

    assert deployer.crv.removeTokenFromVirtualLP(dai.address)
    assert deployer.crv.removeTokenFromVirtualLP(weth.address)
    assert deployer.crv.removeTokenFromVirtualLP(wbtc.address)


# check if our pre-calc for array is rightk
def test_correct_calc_estimation(deployer, accounts, isolation):
    accounts.default = deployer.me
    dai = deployer.tokens.dai
    amount = 1000 * 1e18

    dai.approve(deployer.crv, amount)
    calc = deployer.crv.calculateArrayTokensGivenERC20Tokens(dai, amount)
    tx = deployer.crv.buy(dai, amount)

    assert calc == tx.return_value


def test_buy(deployer, accounts, isolation):
    accounts.default = deployer.me
    for k, v in deployer.tokens.items():
        prev = deployer.array.balanceOf(deployer.me)
        m = min(v.balanceOf(deployer.me), (deployer.bpool.getBalance(v.address))/2 - 1000)
        tx = deployer.crv.buy(v.address, m)
        aft = deployer.array.balanceOf(deployer.me)
        assert int(tx.return_value) == (aft - prev)


def test_revert_no_balance(deployer, accounts, isolation):
    accounts.default = accounts[0]
    buy = 1000e18
    coin = deployer.tokens['dai']
    coin.transfer(ZERO_ADDRESS, coin.balanceOf(accounts[0]))
    coin.approve(deployer.crv, buy)
    with brownie.reverts("dev: user balance < amount"):
        deployer.crv.buy(coin, buy, {'from' : accounts[0]})
