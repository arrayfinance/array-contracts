from brownie import *

#
# network.connect( 'mainnet-fork' )
# project.load('..', 'ArrayContractsProject')
#
# me = accounts.default = accounts[0]
# crpf = Contract.from_explorer( '0xed52D8E202401645eDAD1c0AA21e872498ce47D0' )
# weth = Token.token_info( 'WETH' )
# dai = Token.token_info( 'DAI' )
# usdc = Token.token_info( 'USDC' )
#
# router = Contract.from_explorer( '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D' )
# router.swapExactETHForTokens( 0, [weth, dai], me.address, int( time.time() ) + 1000, {'value': '5 ether'} )
# router.swapExactETHForTokens( 0, [weth, usdc], me.address, int( time.time() ) + 1000, {'value': '5 ether'} )
#
# PoolParams = ['ARRAYLP', 'Array LP', [usdc, dai], [1e6, 1e18], [25e18, 25e18], 1e14]
# PoolRights = [True, True, True, True, False, True]
# pool = crpf.newCrp( '0x9424B1412450D0f8Fc2255FAf6046b98213B76Bd', PoolParams, PoolRights )
# usdc = Contract.from_explorer(usdc)
# dai = Contract.from_explorer(dai)
# poolcontract = project.ArrayContractsProject.interface.pool( pool.return_value )
# usdc.approve(poolcontract.address, 2**256-1)
# dai.approve(poolcontract.address, 2**256-1)
# crp = poolcontract.createPool(100*1e18)
