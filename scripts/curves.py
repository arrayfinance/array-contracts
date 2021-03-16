from brownie import *

project.load('../')


from brownie.project.ArrayContractsProject import *

network.connect( 'kovan' )
me = accounts.default = accounts.load('boobies')

# at = ArrayToken.deploy( 'ArrayToken', 'ARRAY', me.address )
# array = at.address
aweth = interface.erc20('0x87b1f4cf9bd63f7bbd3ee1ad04e8f52540349347')
adai = interface.erc20('0xdcf0af9e59c002fa3aa091a46196b37530fd48a8')
awbtc = interface.erc20('0x62538022242513971478fcc7fb27ae304ab5c29f')
ausdc = interface.erc20('0xe12afec5aa12cf614678f9bfeeb98ca9bb95b5b0')

print(aweth.balanceOf(me), adai.balanceOf(me), awbtc.balanceOf(me), ausdc.balanceOf(me))



# crpf = Contract.from_explorer( '0x53265f0e014995363AE54DAd7059c018BaDbcD74' )
#
# PoolParams = ['ARRAYLP', 'Array LP', [weth, dai], [Wei( 49 ), Wei( 49 )], [Wei( 49 ), Wei( 49 )], 0.01 * 1e18]
# Rights = [True, True, True, True, True, True]
#
# tx = crpf.newCrp( '0x8f7F78080219d4066A8036ccD30D588B416a40DB', PoolParams, Rights )
#
# weth = Contract.from_explorer( weth )
# dai = Contract.from_explorer( dai )
# weth.approve( pool.address, 2 ** 256 - 1 )
# dai.approve( pool.address, 2 ** 256 - 1 )
#
# pool.createPool( 100 * 1e18 )
