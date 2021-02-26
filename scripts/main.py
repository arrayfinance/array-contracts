from brownie import ArrayFactory, ArrayProxyAdmin, ArrayProxyAdminTimelock, ArrayVault, accounts, address

deployer = accounts[0]
owner = accounts[1]

af = deployer.deploy(ArrayFactory)
apa = deployer.deploy(ArrayProxyAdmin)
apat = deployer.deploy(ArrayProxyAdminTimelock(86400, [owner.address, deployer.address], address(0)) )
av = deployer.deploy(ArrayVault)

