// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./ArrayVault.sol";
import "openzeppelin-contracts/contracts/utils/Create2.sol";
import "openzeppelin-contracts/contracts/utils/Address.sol";
import "openzeppelin-contracts/contracts/proxy/TransparentUpgradeableProxy.sol";

contract ArrayFactory {
    event ProxyCreated(address proxyAddress);
    event VaultCreated(address implementation);

    function deployProxyWithImplementation(bytes32 salt, address proxyAdminAddress) public {
        address proxyAddress;
        address vaultAddress;

        // here we're taking care of the *implementation*
        vaultAddress = Create2.deploy(0, salt, type(ArrayVault).creationCode);

        // here we're taking care of the *implementation*
        // deploy proxy with the vaultAddress
        TransparentUpgradeableProxy proxy =
        new TransparentUpgradeableProxy(
            vaultAddress,
            proxyAdminAddress,
            ''
        );

        proxyAddress = address(proxy);

        ArrayVault(vaultAddress).initialize(msg.sender);
        emit VaultCreated(vaultAddress);
    }

}
