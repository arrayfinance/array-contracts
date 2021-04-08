from brownie import *
from scripts.create_smartpool import *
from scripts.tokens import *

# tokens

tokens = {
        'dai'   : interface.ERC20( '0x6b175474e89094c44da98b954eedeac495271d0f' ),
        'usdc'  : interface.ERC20( '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' ),
        'wbtc'  : interface.ERC20( '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599' ),
        'renbtc': interface.ERC20( '0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D' ),
        'weth'  : interface.weth9( '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' )
        }

# whales

whales = {
        'dai'   : accounts.at( '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643', force=True ),
        'usdc'  : accounts.at( '0x39aa39c021dfbae8fac545936693ac917d5e7563', force=True ),
        'wbtc'  : accounts.at( '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4', force=True ),
        'renbtc': accounts.at( '0x93054188d876f558f4a66B2EF1d97d16eDf0895B', force=True ),
        'weth'  : accounts.at( '0x31114D954EC577bfA739d545b2dbf000d7AA66D0', force=True )
        }

# deployer

me = accounts.default = accounts[0]

# deploy contracts
array_token = ArrayToken.deploy( 'ArrayToken', 'ARRAY', ZERO_ADDRESS )
bancor = BancorFormula.deploy()

# import bancor smart pool
spool = main()
curve = Curve.deploy( me, me, array_token, bancor, spool )

# initialize contracts

initial_lp_tokens = spool.totalSupply()
spool.approve( curve.address, initial_lp_tokens, {'from': me} )
array_token.grantRole( array_token.MINTER_ROLE(), curve.address, {'from': me} )
array_token.grantRole( array_token.BURNER_ROLE(), curve.address, {'from': me} )
curve.initialize( initial_lp_tokens, {'from': me} )

# send deployer 1000 dai
tokens['dai'].transfer( me, 1000e18, {'from': whales['dai']} )

# allow curve contract to spend my 1000 dai
tokens['dai'].approve( curve, 1000e18, {'from': me} )

for t in tokens.values():
    curve.addTokenToVirtualLP( t )
