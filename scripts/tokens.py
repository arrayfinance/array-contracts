from brownie import *
from dotmap import DotMap

tokens = DotMap( {
        'dai'   : interface.ERC20( '0x6b175474e89094c44da98b954eedeac495271d0f' ),
        'usdc'  : interface.ERC20( '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' ),
        'wbtc'  : interface.ERC20( '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599' ),
        'renbtc': interface.ERC20( '0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D' ),
        'weth'  : interface.weth9( '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' )
        } )
