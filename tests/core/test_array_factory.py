import brownie


# a basic test to check our logic on how to upgrade contracts using the ERC1967 standard and UUPS (OpenZeppelin)
# Mock has one variable 'something' that is set to a value when the contract is being initialized,
# and MockExtended has the exact same code but adds a variable 'something_else' **after** the prevoius one in the code,
# it also has a second function to initialize this variable since we cannot re-use initialize(), given that
# it's protected by OZs Initializable modifier, the test shows
def test_upgrade_proxy(accounts, factory, Mock, MockExtended, developer):
    accounts.default = developer

    # the implementation of our main contract
    mock = Mock.deploy()

    # put it behind a ERC1967 proxy
    txn = factory.deployProxy(mock)

    # we have to use the logic of the extended mock contract to wrap around the proxy address,
    # however the extended part of the contract (something_else) isn't accessible
    mock_proxied = MockExtended.at(txn.return_value)

    # make sure the implementation is set correctly
    assert mock_proxied.getImplementation() == mock.address

    # let's initialize it
    mock_proxied.initialize('Hello')

    # something should return Hello
    assert mock_proxied.something() == 'Hello'

    # but something_else shouldn't exist, it should revert since we didn't extend/upgrade the contract yet
    with brownie.reverts():
        mock_proxied.something_else()

    # now we deploy the implementation of the upgrade
    # it adds a variable something_else (**AFTER** something) without any value
    mock_extended = MockExtended.deploy()

    # encode the call to the function that sets the value of something_else
    calldata = mock_extended.extend.encode_input('World')

    # upgrade and call the function on the new implementation
    mock_proxied.upgradeToAndCall(mock_extended, calldata)

    # we didn't set this variable in the new implementation, but it should still hold the value that was set
    # when the first implementation was initialized
    assert mock_proxied.something() == 'Hello'

    # this is the variable that was added in the upgrade and now it should be set
    assert mock_proxied.something_else() == 'World'

    # so the proxy storagae kept the value that was set when the first implementation was
    # initialized and we successfully extended the storage of the proxy by upgrading the contract
    # and adding another variable and setting it to a different value
