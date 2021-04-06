from brownie import *
from dotmap import DotMap

if len( project.get_loaded_projects() ) == 0:
    p = project.load( name='ArrayContractsProject' )
    p.load_config()
    network.connect( 'mainnet-fork' )
    from brownie.project.ArrayContractsProject import interface

POOL_VALUE = 700_000  # in dai
POOL_TOKENS = 333_333

token = ['dai', 'usdc', 'wbtc', 'renbtc', 'weth']

inyourfaces = {
        'dai'   : interface.ERC20( '0x6b175474e89094c44da98b954eedeac495271d0f' ),
        'usdc'  : interface.ERC20( '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' ),
        'wbtc'  : interface.ERC20( '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599' ),
        'renbtc': interface.ERC20( '0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D' ),
        'weth'  : interface.weth9( '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' )
        }

uniswap_pairs = {
        'dai'   : interface.pair( '0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11' ),
        'usdc'  : interface.pair( '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc' ),
        'wbtc'  : interface.pair( '0xBb2b8038a1640196FbE3e38816F3e67Cba72D940' ),
        'renbtc': interface.pair( '0x81fbef4704776cc5bba0a5df3a90056d2c6900b3' )
        }

weight = {
        'dai': 0.17, 'usdc': 0.17, 'wbtc': 0.165, 'renbtc': 0.165, 'weth': 0.33
        }

whales = {
        'dai'   : accounts.at( '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643', force=True ),
        'usdc'  : accounts.at( '0x39aa39c021dfbae8fac545936693ac917d5e7563', force=True ),
        'wbtc'  : accounts.at( '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4', force=True ),
        'renbtc': accounts.at( '0x93054188d876f558f4a66B2EF1d97d16eDf0895B', force=True ),
        'weth'  : accounts.at( '0x31114D954EC577bfA739d545b2dbf000d7AA66D0', force=True )
        }


def get_prices_in_eth(symbol):
    if symbol == 'weth':
        return 1

    decimals = inyourfaces[symbol].decimals()
    pair = uniswap_pairs[symbol]
    weth = inyourfaces['weth'].address
    r = pair.getReserves()

    eth_price = 0

    if pair.token0() == weth:
        p0 = r[0] / 1e18
        p1 = r[1] / (10 ** decimals)
        eth_price = p1 / p0
    elif pair.token1() == weth:
        p0 = r[0] / (10 ** decimals)
        p1 = r[1] / 1e18
        eth_price = p0 / p1

    return eth_price


def get_prices_in_token(t1, t2):
    return get_prices_in_eth( t1 ) / get_prices_in_eth( t2 )


def create_map():
    d = DotMap()

    for k in token:
        d[k].contract = inyourfaces[k]
        d[k].pair = uniswap_pairs[k] if k != 'weth' else None
        d[k].weight = weight[k]
        d[k].eth_price = get_prices_in_eth( k )
        d[k].dai_price = get_prices_in_token( 'dai', k )
        d[k].decimals = d[k].contract.decimals()
        d[k].whale = whales[k]
        d[k].balance = d[k].weight * 10 ** d[k].decimals * (POOL_VALUE / d[k].dai_price)
    return d


def main():
    d = create_map()

    someguy = accounts.default = accounts[2]

    for k in token:
        d[k].contract.transfer( someguy, d[k].balance, {'from': d[k].whale} )

    pool_params = ['ARRAYLP', 'Array LP', [d[k].contract.address for k in token], [d[k].balance for k in token],
                   [d[k].weight * 1e19 for k in token], 1e14]

    pool_rights = [True, True, True, True, False, True]

    crpfact = interface.fact( '0xed52D8E202401645eDAD1c0AA21e872498ce47D0' )
    tx = crpfact.newCrp( '0x9424B1412450D0f8Fc2255FAf6046b98213B76Bd', pool_params, pool_rights )
    spool = interface.pool( tx.return_value )

    for k in token:
        d[k].contract.approve( spool.address, 2 ** 256 - 1 )

    spool.createPool( POOL_TOKENS * 1e18 )
    spool.setCap( 1e28 )

    return spool


def get_bpool(spool):
    return interface.bpool( spool.bPool() )


def pool_in(spool, factor):
    m = 2 ** 256 - 1
    spool.joinPool( factor, [m, m, m, m, m] )


def pool_out(spool, factor):
    m = 0
    spool.exitPool( factor, [m, m, m, m, m] )


def dai_pool_add(spool, a):
    d = create_map()

    for k in token:
        b = d[k].weight * d[k].price * d[k].dai_price * d[k].decimals * a
        spool.joinswapExternAmountIn( d[k].contract.address, b, 0 )

    return calc_bal( get_bpool( spool ) )


def dai_pool_remove(spool, a):
    d = create_map()

    for k in token:
        b = d[k].weight * d[k].price * d[k].dai_price * d[k].decimals * a
        spool.exitswapExternAmountOut( d[k].contract.address, b, 2 ** 256 - 1 )

    return calc_bal( get_bpool( spool ) )


def calc_bal(bpool):
    d = create_map()
    s = 0

    for k in token:
        s += bpool.getBalance( d[k].contract.address ) * d[k].dai_price / 10 ** d[k].decimals

    return s
