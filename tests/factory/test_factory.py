import pytest
import brownie
from brownie import chain


# owner should be able to deploy a new proxy contract
def test_deploy_authorized(af, apa, owner, vault, ini):
    af.deployProxy( apa.address, vault.address, ini, {'from': owner} )


# reverts
# someguy should NOT be able to deploy a new proxy contract
def test_deploy_reverts_unauthorized(af, apa, someguy, vault, ini):
    with brownie.reverts( 'Ownable: caller is not the owner' ):
        af.deployProxy( apa.address, vault.address, ini, {'from': someguy} )


# reverts
# implementation address MUST BE contract
def test_deploy_reverts_implementation_not_contract(af, apa, owner, ini):
    with brownie.reverts( 'dev: implementation must be contract' ):
        af.deployProxy( apa.address, owner.address, ini, {'from': owner} )


# deploy proxy should return the address of the proxy containing the logic of it's implementation
def test_deploy_check_for_return_value(ArrayVault, af, apa, owner, vault, ini):
    tx = af.deployProxy( apa.address, vault.address, ini, {'from': owner} )
    # we assign the ArrayVault contract (not the already deployed one!!) to the proxy address
    # and check t hat it indeed points to a contract
    v = ArrayVault.at( tx.return_value )
    assert type( v ) == brownie.network.contract.ProjectContract


# an event, containing the proxy address should be emitted when a proxy is deployed
def test_deploy_event(af, apa, owner, vault, ini):
    tx = af.deployProxy( apa.address, vault.address, ini, {'from': owner} )
    assert len( tx.events ) == 1
    assert tx.events[0].name == 'ProxyCreated'
    assert tx.events[0]['proxyAddress'] == tx.return_value


# implementation should be correctly initialized when deployed
def test_deploy_initialization_correct(ArrayVault, af, apa, owner, vault, ini):
    tx = af.deployProxy( apa.address, vault.address, ini, {'from': owner} )
    v = ArrayVault.at( tx.return_value )
    assert v.owner() == owner.address


# proxyadmin should to be a contract
def test_deploy_reverts_noinitialization(af, apa, owner, vault):
    with brownie.reverts( 'dev: we want to initialize as soon as possible' ):
        af.deployProxy( apa.address, vault.address, b'', {'from': owner} )


# initialization code should not be empty, we wan't to initialize as soon as possible
def test_deploy_reverts_noadmin(af, vault, owner, ini, someguy):
    with brownie.reverts( 'dev: proxyAdmin must be contract' ):
        af.deployProxy( someguy.address, vault.address, ini, {'from': owner} )


# admin of the deployed proxy should be the admin contract
def test_deploy_check_admin(af, apa, vault, owner, ini):
    tx = af.deployProxy( apa.address, vault.address, ini, {'from': owner} )
    assert apa.getProxyAdmin( tx.return_value ) == apa.address


# implementation of deployed proxy should be the implementation
def test_deploy_check_implementation(af, apa, vault, owner, ini):
    tx = af.deployProxy( apa.address, vault.address, ini, {'from': owner} )
    assert apa.getProxyImplementation( tx.return_value ) == vault.address


# sanity checks, fixtures are correct
def test_timelock_sanity(apat, owner, someguy):
    assert apat.hasRole( apat.PROPOSER_ROLE(), owner.address )
    assert apat.hasRole( apat.EXECUTOR_ROLE(), someguy.address )


# create a proxy, encode upgradecall for changing the implementation, schedule it in the timelock,
# advance chain 24hs, execute and verify new implementation
def test_timelock_upgrade_proxy(af, apat, apa, owner, someguy, ini, vault, vault_two):
    tx = af.deployProxy( apa.address, vault_two.address, ini, {'from': owner} )
    proxy_address = tx.return_value
    implementation_data = apa.upgrade.encode_input( proxy_address, vault_two.address )
    apat.schedule( apa.address, 0, implementation_data, '', '', 86400, {'from': owner} )
    chain.sleep( 86450 )
    apat.execute( apa.address, 0, implementation_data, '', '', {'from': someguy} )
    assert apa.getProxyImplementation( proxy_address ) == vault_two.address
