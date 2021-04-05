from brownie import *
from dotmap import DotMap
from rich.console import Console

POOL_VALUE = 7  # in hundred thousand
POOL_TOKENS = 333  # in k


def main():
    console = Console()

    dai = interface.ERC20( '0x6b175474e89094c44da98b954eedeac495271d0f' )
    usdc = interface.ERC20( '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' )
    wbtc = interface.ERC20( '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599' )
    renbtc = interface.ERC20( '0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D' )
    weth = interface.weth9( '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' )

    p = DotMap()
    p.renbtc = interface.pair( '0x81fbef4704776cc5bba0a5df3a90056d2c6900b3' )
    p.wbtc = interface.pair( '0xBb2b8038a1640196FbE3e38816F3e67Cba72D940' )
    p.dai = interface.pair( '0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11' )
    p.usdc = interface.pair( '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc' )

    q = DotMap()
    for k, v in p.items():
        token0 = interface.ERC20( v.token0() )
        token1 = interface.ERC20( v.token1() )
        r = v.getReserves()
        d = [token0.decimals(), token1.decimals()]
        # check that the token we divide by is eth
        if token0.symbol().lower() == 'weth':
            i, j = 1, 0
        else:
            i, j = 0, 1
        result = (r[i] / 10 ** d[i]) / (r[j] / 10 ** d[j])
        q[k] = result

    dm = DotMap()

    a = POOL_VALUE * 1e5 / 1.6999992549442997

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
    accounts[3].transfer( someguy, amount=100e18 )
    accounts[4].transfer( someguy, amount=100e18 )
    accounts[5].transfer( someguy, amount=100e18 )
    accounts[6].transfer( someguy, amount=100e18 )
    accounts[7].transfer( someguy, amount=100e18 )
    accounts[8].transfer( someguy, amount=100e18 )
    weth.deposit( {'from': someguy, 'value': 700e18} )

    tokens = [_.address for _ in dm.contracts.values()]
    balances = [_ for _ in dm.balances.values()]
    weights = [_ * 1e19 for _ in dm.weights.values()]
    PoolParams = ['ARRAYLP', 'Array LP', tokens, balances, weights, 1e14]
    PoolRights = [True, True, True, True, False, True]
    crpfact = interface.fact( '0xed52D8E202401645eDAD1c0AA21e872498ce47D0' )
    tx = crpfact.newCrp( '0x9424B1412450D0f8Fc2255FAf6046b98213B76Bd', PoolParams, PoolRights )
    poolcontract = interface.pool( tx.return_value )

    for _ in dm.contracts.values():
        _.approve( poolcontract.address, 2 ** 256 - 1 )

    poolcontract.createPool( POOL_TOKENS * 1e20 )
    poolcontract.setCap( 1e28 )

    bpool = interface.bpool( poolcontract.bPool() )

    while True:

        # try:
        adjust_pool( poolcontract, usdc, dai, weth, wbtc, renbtc, dm )
        # except Exception:
        #     continue
        # else:
        value = calc_bal( poolcontract, bpool, console, usdc, dai, weth, wbtc, renbtc, dm )
        value = value / 1e23
        # finally:
        if round( value, 4 ) == POOL_VALUE:
            console.print( f'\nPool value: {value * 10 ** 5} DAI' )
            console.print( f'Pool tokens: {poolcontract.totalSupply() / 1e18} ' )
            break
        else:
            continue

    return poolcontract


def adjust_pool(poolcontract, usdc, dai, weth, wbtc, renbtc, dm):
    for i in range( 0, 3 ):
        poolcontract.joinswapExternAmountIn( usdc.address, dm.balances.usdc / 10, 0, {'from': accounts[2]} )
        poolcontract.joinswapExternAmountIn( dai.address, dm.balances.dai / 10, 0, {'from': accounts[2]} )
        poolcontract.joinswapExternAmountIn( weth.address, dm.balances.weth / 10, 0, {'from': accounts[2]} )
        poolcontract.joinswapExternAmountIn( wbtc.address, dm.balances.wbtc / 10, 0, {'from': accounts[2]} )
        poolcontract.joinswapExternAmountIn( renbtc.address, dm.balances.renbtc / 10, 0, {'from': accounts[2]} )


def calc_bal(poolcontract, bpool, console, usdc, dai, weth, wbtc, renbtc, dm):
    a = bpool.getBalance( weth ) * dm.prices.weth
    b = bpool.getBalance( wbtc ) * dm.prices.wbtc
    c = bpool.getBalance( renbtc ) * dm.prices.renbtc
    d = bpool.getBalance( dai ) * dm.prices.dai
    e = bpool.getBalance( usdc ) * dm.prices.usdc

    totaleth = a + b + c + d + e
    total_dai = totaleth * dm.prices.dai
    return total_dai
