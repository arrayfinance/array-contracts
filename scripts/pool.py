from brownie import *
from rich import pretty
from dotmap import DotMap
import time

pretty.install()
project.load( name='ArrayContractsProject' )
from brownie.project.ArrayContractsProject import interface

network.connect( 'mainnet-fork' )
uni = interface.router02( '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D' )

whales = DotMap()
whales.dai = accounts.at( '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643', force=True )
whales.usdc = accounts.at( '0x39aa39c021dfbae8fac545936693ac917d5e7563', force=True )
whales.wbtc = accounts.at( '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4', force=True )
whales.renbtc = accounts.at( '0x93054188d876f558f4a66B2EF1d97d16eDf0895B', force=True )

c = DotMap()

c.ren = interface.ERC20( '0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D' )
c.wbtc = interface.ERC20( '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599' )
c.dai = interface.ERC20( '0x6B175474E89094C44Da98b954EedeAC495271d0F' )
c.usdc = interface.ERC20( '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' )
c.weth = interface.weth9( '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' )

p = DotMap()
p.ren = interface.pair( '0x81fbef4704776cc5bba0a5df3a90056d2c6900b3' )
p.wbtc = interface.pair( '0xBb2b8038a1640196FbE3e38816F3e67Cba72D940' )
p.dai = interface.pair( '0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11' )
p.usdc = interface.pair( '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc' )


def getprice(pair):
    token0 = interface.ERC20( pair.token0() )
    token1 = interface.ERC20( pair.token1() )
    r = pair.getReserves()
    d = [token0.decimals(), token1.decimals()]
    # check that the token we divide by is eth
    if token0.symbol().lower() == 'weth':
        i, j = 1, 0
    else:
        i, j = 0, 1

    result = (r[i] / 10 ** d[i]) / (r[j] / 10 ** d[j])
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

for t in c.values():


c.weth.deposit( {'value': '100 ether'} )

PoolParams = ['ARRAYLP', 'Array LP', tokens, [_ for _ in balances.values()], weights_norm, 5e14]
PoolRights = [True, True, True, True, False, True]
crpfact = interface.fact( '0xed52D8E202401645eDAD1c0AA21e872498ce47D0' )
tx = crpfact.newCrp( '0x9424B1412450D0f8Fc2255FAf6046b98213B76Bd', PoolParams, PoolRights )
po = interface.pool( tx.return_value )

c.weth.approve( po.address, 2 ** 256 - 1 )
c.dai.approve( po.address, 2 ** 256 - 1 )
# c.ren.approve( po.address, 2 ** 256 - 1 )
# c.usdc.approve( po.address, 2 ** 256 - 1 )
# c.wbtc.approve( po.address, 2 ** 256 - 1 )
#
# po.createPool( 100e18 )
# bp = interface.bpool( po.bPool() )
#
#
# def getbalances():
#     for key, value in c.items():
#         dec = value.decimals()
#         bal = bp.getBalance( value.address ) / 10 ** dec
#         print( f'{key} : {bal:.4f}' )
#
#
# print( f'SmartPool deployed at: {po.address}\n' )
# print( f'Balancer pool total supply: {po.totalSupply() / 1e18}' )
# print( f'Balancer pool token balances:' )
# getbalances()
