from hexbytes import HexBytes
import pytest
import brownie
from brownie import ZERO_ADDRESS


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_deploy_requires(factory, governance, mock):
    test = HexBytes('0xb00b')

    with brownie.reverts('dev: proxyAdmin must be contract'):
        factory.deployProxy(ZERO_ADDRESS, mock, test)

    with brownie.reverts('dev: implementation must be contract'):
        factory.deployProxy(mock, ZERO_ADDRESS, test)

    with brownie.reverts('dev: we want to initialize as soon as possible'):
        factory.deployProxy(mock, mock, HexBytes(''))


# an event, containing the proxy address should be emitted when a proxy is deployed
def test_deploy_event(factory, mock, ArrayProxyAdmin, governance, developer, user, timelock):
    apa = ArrayProxyAdmin.deploy(timelock, {'from': developer})
    init = mock.initialize.encode_input(user)
    tx = factory.deployProxy(apa, mock, init, {'from': developer})
    assert len(tx.events) > 0
    assert tx.events[-1].name == 'ProxyCreated'
    assert tx.events[-1]['proxyAddress'] == tx.return_value
