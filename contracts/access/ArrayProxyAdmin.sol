// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "../../node_modules/@openzeppelin/contracts/proxy/transparent/ProxyAdmin.sol";

contract ArrayProxyAdmin is ProxyAdmin {
    constructor(address _timelock){
        transferOwnership(_timelock);
    }
}


