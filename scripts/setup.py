from brownie import *


def get_curve():
    from scripts.create_smartpool import get_spool
    from scripts.tokens import tokens
    # deployer

    me = accounts.default = accounts[0]

    # deploy contracts
    array_token = ArrayToken.deploy( 'ArrayToken', 'ARRAY', ZERO_ADDRESS )
    bancor = BancorFormula.deploy()

    # import bancor smart pool
    spool = get_spool()
    curve = Curve.deploy( me, me, array_token, bancor, spool )

    # initialize contracts

    initial_lp_tokens = spool.totalSupply()
    spool.approve( curve.address, initial_lp_tokens, {'from': me} )
    array_token.grantRole( array_token.MINTER_ROLE(), curve.address, {'from': me} )
    array_token.grantRole( array_token.BURNER_ROLE(), curve.address, {'from': me} )
    curve.initialize( initial_lp_tokens, {'from': me} )

    for t in tokens.values():
        curve.addTokenToVirtualLP( t.address )

    return curve
