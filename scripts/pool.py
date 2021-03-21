from brownie import *
from dataclasses import dataclass, asdict
from dotmap import DotMap
from w3helpers import Token, Uniswap
import time

network.connect( 'mainnet-fork' )
project.load( name='ArrayContractsProject' )

from brownie.project.ArrayContractsProject import interface

t = Token()

uni = interface.router02( '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D' )

c = DotMap()

c.ren = interface.ERC20( t.token_info( 'renBTC' ) )
c.wbtc = interface.ERC20( t.token_info( 'wbtc' ) )
c.dai = interface.ERC20( t.token_info( 'dai' ) )
c.usdc = interface.ERC20( t.token_info( 'usdc' ) )
c.weth = interface.weth9( t.token_info( 'weth' ) )

p = DotMap()

p.ren = interface.pair( '0x81fbef4704776cc5bba0a5df3a90056d2c6900b3' )
p.wbtc = interface.pair( '0xBb2b8038a1640196FbE3e38816F3e67Cba72D940' )
p.dai = interface.pair( '0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11' )
p.usdc = interface.pair( '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc' )


def getprice(pair):
    token0 = interface.ERC20( pair.token0() )
    dec0 = token0.decimals()
    token1 = interface.ERC20( pair.token1() )
    dec1 = token1.decimals()
    r = pair.getReserves()
    result = (r[1] / 10 ** dec1) / (r[0] / 10 ** dec0)
    if token0.symbol().lower() in ['wbtc', 'dai', 'usdc']:
        return 1 / result
    else:
        return result


prices = {'weth': 1}
for k, v in p.items():
    prices[k] = getprice( v )

balances = {}
balances['weth'] = prices['weth'] * 0.33 * 20e18
balances['wbtc'] = prices['wbtc'] * 0.165 * 20e8
balances['ren'] = prices['ren'] * 0.165 * 20e8
balances['dai'] = prices['dai'] * 0.17 * 20e18
balances['usdc'] = prices['usdc'] * 0.17 * 20e6

me = accounts.default = accounts[0]

weights = {
        'weth': 33 / 2.5, 'wbtc': 16.5 / 2.5, 'renbtc': 16.5 / 2.5, 'dai': 17 / 2.5, 'usdc': 17 / 2.5
        }

weights_norm = [i * 1e18 for i in weights.values()]
tokens = [c.weth.address, c.wbtc.address, c.ren.address, c.dai.address, c.usdc.address]

for i in range( 0, 9, 1 ):
    accounts[i].transfer( to=me, amount='100 ether' )

for i in tokens[1:]:
    uni.swapExactETHForTokens( 0, [c.weth.address, i], me.address, int( time.time() ) + 1000,
                               {'from': me.address, 'value': '100 ether'} )

c.weth.deposit( {'value': '100 ether'} )

PoolParams = ['ARRAYLP', 'Array LP', tokens, [_ for _ in balances.values()], weights_norm, 5e14]
PoolRights = [True, True, True, True, False, True]
crpfact = interface.fact( '0xed52D8E202401645eDAD1c0AA21e872498ce47D0' )
tx = crpfact.newCrp( '0x9424B1412450D0f8Fc2255FAf6046b98213B76Bd', PoolParams, PoolRights )
poolcontract = interface.pool( tx.return_value )

c.weth.approve( poolcontract.address, 2 ** 256 - 1 )
c.dai.approve( poolcontract.address, 2 ** 256 - 1 )
c.ren.approve( poolcontract.address, 2 ** 256 - 1 )
c.usdc.approve( poolcontract.address, 2 ** 256 - 1 )
c.wbtc.approve( poolcontract.address, 2 ** 256 - 1 )

poolcontract.createPool( 100e18 )

