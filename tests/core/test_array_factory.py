import eth_abi
from brownie.convert import to_bytes
from eth_utils import to_checksum_address
from web3 import Web3
from hexbytes import HexBytes
import pytest
import brownie
from brownie import ZERO_ADDRESS
from eth_utils import encoding


@pytest.fixture(scope='module')
def factory(governance, ArrayFactory):
    yield ArrayFactory.deploy({'from': governance})


@pytest.fixture(scope='module')
def token(governance, ArrayToken):
    yield ArrayToken.deploy('Array Finance', 'ARRAY', {'from': governance})


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_reverts(factory, governance, token):
    test = HexBytes('0xb00b')

    with brownie.reverts('dev: proxyAdmin must be contract'):
        factory.deployProxy(ZERO_ADDRESS, token.address, test)

    with brownie.reverts('dev: implementation must be contract'):
        factory.deployProxy(token.address, ZERO_ADDRESS, test)

    with brownie.reverts('dev: we want to initialize as soon as possible'):
        factory.deployProxy(token.address, token.address, HexBytes(''))


def test_deploy(factory, accounts, governance, ArrayProxyAdmin, ArrayVault):
    accounts.default = governance
    av = ArrayVault.deploy()
    apa = ArrayProxyAdmin.deploy()
    init = av.initialize.encode_input(governance)
    factory.deployProxy(apa.address, av.address, init)


# an event, containing the proxy address should be emitted when a proxy is deployed
def test_deploy_event(factory, ArrayVault, ArrayProxyAdmin, governance):
    av = ArrayVault.deploy()
    apa = ArrayProxyAdmin.deploy()
    init = av.initialize.encode_input(governance)
    tx = factory.deployProxy(apa.address, av.address, init, {'from': governance})
    assert len(tx.events) == 1
    assert tx.events[0].name == 'ProxyCreated'
    assert tx.events[0]['proxyAddress'] == tx.return_value
