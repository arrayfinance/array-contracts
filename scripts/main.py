from brownie import *

# network.connect( 'ropsten' )

owner = accounts.load('ropsten_owner')

af = owner.deploy( ArrayFactory, publish_source=True)
apa = owner.deploy( ArrayProxyAdmin , publish_source=True)
apat = owner.deploy( ArrayProxyAdminTimelock, 6400, [owner], [owner, ZERO_ADDRESS] , publish_source=True)
av = owner.deploy( ArrayVault, publish_source=True )


print('AF ' + af.address, 'APA ' + apa.address, 'APAT ' + apat.address, 'AV ' + av.address)
