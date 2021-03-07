// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/governance/TimelockController.sol";

contract ArrayProxyAdminTimelock is TimelockController {
    constructor(uint256 minDelay, address[] memory proposers, address[] memory executors) public
    TimelockController(minDelay, proposers,executors) {}
}
