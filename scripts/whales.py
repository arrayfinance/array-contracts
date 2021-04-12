from brownie import *
from dotmap import DotMap
from scripts.tokens import tokens

whales = DotMap({
    'dai': [accounts.at('0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503', force=True),
            accounts.at('0x13aec50f5D3c011cd3fed44e2a30C515Bd8a5a06', force=True), accounts.at('0x16463c0fdB6BA9618909F5b120ea1581618C1b9E', force=True)],
    'usdc': [accounts.at('0x39aa39c021dfbae8fac545936693ac917d5e7563', force=True)],
    'wbtc': [accounts.at('0xc11b1268c1a384e55c48c2391d8d480264a3a7f4', force=True)],
    'renbtc': [accounts.at('0x93054188d876f558f4a66B2EF1d97d16eDf0895B', force=True)],
    'weth': [accounts.at('0x31114D954EC577bfA739d545b2dbf000d7AA66D0', force=True)]
})


def make_me_rich():
    me = accounts[0]
    for w in whales['dai']:
        tokens.dai.transfer(me, tokens.dai.balanceOf(w), {'from': w})
    return me
