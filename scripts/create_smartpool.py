from brownie import *
from dotmap import DotMap
from rich.console import Console
from brownie.project.ArrayContractsProject import interface

POOL_VALUE = 700_000  # in dai
POOL_TOKENS = 333_333

dai = interface.ERC20( '0x6b175474e89094c44da98b954eedeac495271d0f' )
usdc = interface.ERC20( '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' )
wbtc = interface.ERC20( '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599' )
renbtc = interface.ERC20( '0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D' )
weth = interface.weth9( '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' )

dm = DotMap()


def get_prices_in_eth(contract):
    token0 = interface.ERC20( contract.token0() )
    token1 = interface.ERC20( contract.token1() )
    r = contract.getReserves()
    d = [token0.decimals(), token1.decimals()]
    # check that the token we divide by is eth
    if token0.symbol().lower() == 'weth':
        i, j = 1, 0
    else:
        i, j = 0, 1
    return (r[i] / 10 ** d[i]) / (r[j] / 10 ** d[j])


def main():
    p = DotMap()
    p.renbtc = interface.pair( '0x81fbef4704776cc5bba0a5df3a90056d2c6900b3' )
    p.wbtc = interface.pair( '0xBb2b8038a1640196FbE3e38816F3e67Cba72D940' )
    p.dai = interface.pair( '0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11' )
    p.usdc = interface.pair( '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc' )

    q = DotMap()
    for k, v in p.items():
        q[k] = get_prices_in_eth( v )

    a = POOL_VALUE

    dm.contracts.weth = weth
    dm.contracts.wbtc = wbtc
    dm.contracts.renbtc = renbtc
    dm.contracts.dai = dai
    dm.contracts.usdc = usdc

    dm.weights.weth = 0.33
    dm.weights.wbtc = 0.165
    dm.weights.renbtc = 0.165
    dm.weights.dai = 0.17
    dm.weights.usdc = 0.17

    dm.prices.weth = 1 / q.dai
    dm.prices.wbtc = q.wbtc / q.dai
    dm.prices.renbtc = q.renbtc / q.dai
    dm.prices.dai = q.dai / q.dai
    dm.prices.usdc = q.usdc / q.dai

    dm.balances.weth = dm.weights.weth * dm.prices.weth * 1e18 * a
    dm.balances.wbtc = dm.weights.wbtc * dm.prices.wbtc * 1e8 * a
    dm.balances.renbtc = dm.weights.renbtc * dm.prices.renbtc * 1e8 * a
    dm.balances.dai = dm.weights.dai * dm.prices.dai * 1e18 * a
    dm.balances.usdc = dm.weights.usdc * dm.prices.usdc * 1e6 * a

    whale = DotMap()
    whale.dai = accounts.at( '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643', force=True )
    whale.usdc = accounts.at( '0x39aa39c021dfbae8fac545936693ac917d5e7563', force=True )
    whale.wbtc = accounts.at( '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4', force=True )
    whale.renbtc = accounts.at( '0x93054188d876f558f4a66B2EF1d97d16eDf0895B', force=True )

    someguy = accounts.default = accounts[2]

    dai.transfer( someguy, 1e26, {'from': whale.dai} )
    usdc.transfer( someguy, 1e14, {'from': whale.usdc} )
    renbtc.transfer( someguy, 1e11, {'from': whale.renbtc} )
    wbtc.transfer( someguy, 1e11, {'from': whale.wbtc} )
    for i in range( 3, 9, 1 ):
        accounts[i].transfer( someguy, amount=100e18 )
    weth.deposit( {'from': someguy, 'value': 700e18} )

    tokens = [_.address for _ in dm.contracts.values()]
    balances = [_ for _ in dm.balances.values()]
    weights = [_ * 1e19 for _ in dm.weights.values()]
    pool_params = ['ARRAYLP', 'Array LP', tokens, balances, weights, 1e14]
    pool_rights = [True, True, True, True, False, True]
    crpfact = interface.fact( '0xed52D8E202401645eDAD1c0AA21e872498ce47D0' )
    tx = crpfact.newCrp( '0x9424B1412450D0f8Fc2255FAf6046b98213B76Bd', pool_params, pool_rights )
    spool = interface.pool( tx.return_value )
    for _ in dm.contracts.values():
        _.approve( spool.address, 2 ** 256 - 1 )

    spool.createPool( POOL_TOKENS * 1e18 )
    spool.setCap( 1e28 )

    return spool


def get_bpool(spool):
    return interface.bpool( spool.bPool() )


def adjust_pool_in(spool, factor):
    m = 2 ** 256 - 1
    spool.joinPool( factor, [m, m, m, m, m] )


def adjust_pool_out(spool, factor):
    m = 0
    spool.exitPool( factor, [m, m, m, m, m] )


def calc_bal(bpool, dm):
    a = bpool.getBalance( weth ) / (dm.prices.weth * 1e18)
    b = bpool.getBalance( wbtc ) / (dm.prices.wbtc * 1e8)
    c = bpool.getBalance( renbtc ) / (dm.prices.renbtc * 1e8)
    d = bpool.getBalance( dai ) / (dm.prices.dai * 1e18)
    e = bpool.getBalance( usdc ) / (dm.prices.usdc * 1e6)

    return (a + b + c + d + e) * 1e18
