// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/** @title Array proxy factory. */
contract ArrayProxyFactory is Ownable {
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
    onlyOwner
    returns (address proxyAddress){

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
