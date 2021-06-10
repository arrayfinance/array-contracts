// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/** @title Array proxy factory. */
contract ArrayProxyFactory is Ownable {
    event ProxyCreated(address proxyAddress);

    /**
    * @dev Creates a ERC1967 proxy and sets the implementation to _implementation and
    * initializes it with the calldata in _init.
  */

    function deployProxy(address _implementation)
    public
    onlyOwner
    returns (ERC1967Proxy)
    {

        require(Address.isContract(_implementation)); // dev: implementation must be contract

        // let's deploy a new proxy
        ERC1967Proxy proxy =
        new ERC1967Proxy(_implementation, '');
        emit ProxyCreated(address(proxy));
        return proxy;
    }

}
