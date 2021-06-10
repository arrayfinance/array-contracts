import brownie


def test_access_control(mock_proxied, factory, rogue, AccessControlStorage, developer, daomsig, devmsig, timelock,
                        accounts):
    accounts.default = developer
    acs = AccessControlStorage.deploy()
    tx = factory.deployProxy(acs)

    acs_proxied = AccessControlStorage.at(tx.return_value)
    acs_proxied.initialize(developer, daomsig, devmsig, timelock)

    mock_proxied.initialize('Hello', acs_proxied)
    mock_proxied.restricted()

    with brownie.reverts():
        mock_proxied.restricted({'from': rogue})
