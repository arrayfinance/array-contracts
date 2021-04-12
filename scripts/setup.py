from brownie import *
from scripts.tokens import *
from scripts.whales import *


def get_curve():
    from scripts.create_smartpool import get_spool
    from scripts.tokens import tokens
    # deployer

    me = accounts.default = accounts[0]

    # deploy contracts
    array_token = ArrayToken.deploy('ArrayToken', 'ARRAY', ZERO_ADDRESS)
    bancor = BancorFormula.deploy()

    # import bancor smart pool
    spool = get_spool()
    curve = Curve.deploy(me, me, array_token, bancor, spool)

    # initialize contracts

    initial_lp_tokens = spool.totalSupply()
    spool.approve(curve.address, initial_lp_tokens, {'from': me})
    array_token.grantRole(array_token.MINTER_ROLE(), curve.address, {'from': me})
    array_token.grantRole(array_token.BURNER_ROLE(), curve.address, {'from': me})
    curve.initialize(initial_lp_tokens, {'from': me})

    for t in tokens.values():
        curve.addTokenToVirtualLP(t.address)

    return curve


def set_supply(curve, coin, supply, user):
    bpt = interface.bpool(curve.BP())
    coin.approve(curve, 2 ** 256 - 1, {'from': user})
    while curve.virtualSupply() < curve.MAX_ARRAY_SUPPLY():

        max_buy = (bpt.getBalance(coin) / 2) - 1e18
        if max_buy > coin.balanceOf(user):
            break

        if curve.virtualSupply() + curve.calculateArrayTokensGivenERC20Tokens(coin, max_buy) > supply:
            break
        else:
            curve.buy(coin, max_buy, {'from': user})

    return curve


def ini(supply=15000e18):
    me = make_me_rich()
    c = get_curve()
    set_supply(c, tokens.dai, supply, me)
    return c, me

