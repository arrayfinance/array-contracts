from brownie import *
from dotmap import DotMap

whales = DotMap( {
        'dai'   : accounts.at( '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643', force=True ),
        'usdc'  : accounts.at( '0x39aa39c021dfbae8fac545936693ac917d5e7563', force=True ),
        'wbtc'  : accounts.at( '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4', force=True ),
        'renbtc': accounts.at( '0x93054188d876f558f4a66B2EF1d97d16eDf0895B', force=True ),
        'weth'  : accounts.at( '0x31114D954EC577bfA739d545b2dbf000d7AA66D0', force=True )
        } )
