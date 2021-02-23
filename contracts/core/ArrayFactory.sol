// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "openzeppelin-contracts/contracts/utils/Create2.sol";
import "openzeppelin-contracts/contracts/utils/Address.sol";
import "openzeppelin-contracts/contracts/proxy/TransparentUpgradeableProxy.sol";
import "openzeppelin-contracts/contracts/access/Ownable.sol";
import "openzeppelin-contracts/contracts/math/SafeMAth.sol";

/** @title Array proxy factory. */
contract ArrayFactory is Ownable {
    event ProxyCreated(address proxyAddress);

        /**
        @dev Creates a proxy that is administered by the proxyAdmin contract, contains logic of the
        implementation and is initialized.
        @param proxyAdminAddress Contract address that is used to administer the proxies, from openzeppelin.
        @param implementationAddress Contract address that contains the logic.
        @param initializationCode parameters that are used to initialize the logic code, can't be empty.
        @return proxyAddress the address of the proxy we deployed.
      */

    function deployProxy(address proxyAdminAddress, address implementationAddress, bytes memory initializationCode)
    public
    onlyOwner returns (address proxyAddress){

        require(Address.isContract(implementationAddress)); // dev: implementation must be contract
        require(Address.isContract(proxyAdminAddress)); // dev: proxyAdmin must be contract
        require(initializationCode.length > 0); // dev: we want to initialize as soon as possible

        // let's deploy a new proxy
        TransparentUpgradeableProxy proxy =
        new TransparentUpgradeableProxy(
            implementationAddress,
            proxyAdminAddress,
            initializationCode);

        proxyAddress = address(proxy);

        emit ProxyCreated(proxyAddress);
        return proxyAddress;
    }

}
