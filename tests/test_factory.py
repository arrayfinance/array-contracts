import brownie


# owner should be able to deploy a new proxy contract
def test_deploy_authorized(af, apa, owner, vault, ini):
    af.deployProxy( apa.address, vault.address, ini, {'from': owner} )


# someguy should NOT be able to deploy a new proxy contract
# should revert
def test_deploy_reverts_unauthorized(af, apa, someguy, vault, ini):
    with brownie.reverts( 'Ownable: caller is not the owner' ):
        af.deployProxy( apa.address, vault.address, ini, {'from': someguy} )


# deploying a proxy that has as implementation an address that isnt a contract
# should revert
def test_deploy_reverts_not_contract(af, apa, owner, ini):
    with brownie.reverts( 'dev: implementation must be contract' ):
        af.deployProxy( apa.address, owner.address, ini, {'from': owner} )


def test_deploy_return_value(ArrayVault, af, apa, owner, vault, ini):
    tx = af.deployProxy( apa.address, vault.address, ini, {'from': owner} )
    # we assign the ArrayVault contract (not the already deployed one!!) to the proxy address
    # and check t hat it indeed points to a contract
    v = ArrayVault.at( tx.return_value )
    assert type( v ) == brownie.network.contract.ProjectContract


# let's check that the correct event is emitted
def test_deploy_event(af, apa, owner, vault, ini):
    tx = af.deployProxy( apa.address, vault.address, ini, {'from': owner} )
    assert len( tx.events ) == 1
    assert tx.events[0].name == 'ProxyCreated'
    assert tx.events[0]['proxyAddress'] == tx.return_value


# let's check if the implementation is correctly initialized
def test_deploy_initialization(ArrayVault, af, apa, owner, vault, ini):
    tx = af.deployProxy( apa.address, vault.address, ini, {'from': owner} )
    v = ArrayVault.at( tx.return_value )
    assert v.owner() == owner.address


# proxyAdmin needs to be a contract
def test_deploy_reverts_noinitialization(af, apa, owner, vault):
    with brownie.reverts( 'dev: we want to initialize as soon as possible' ):
        af.deployProxy( apa.address, vault.address, b'', {'from': owner} )


# we want to initialize the implementation as soon as possible
def test_deploy_reverts_noadmin(af, vault, owner, ini, someguy):
    with brownie.reverts( 'dev: proxyAdmin must be contract' ):
        af.deployProxy( someguy.address, vault.address, ini, {'from': owner} )


def test_deploy_check_admin(af, apa, vault, owner, ini):
    tx = af.deployProxy( apa.address, vault.address, ini, {'from': owner} )
    assert apa.getProxyAdmin(tx.return_value) == apa.address


def test_deploy_check_implementation(af, apa, vault, owner, ini):
    tx = af.deployProxy( apa.address, vault.address, ini, {'from': owner} )
    assert apa.getProxyImplementation( tx.return_value ) == vault.address
