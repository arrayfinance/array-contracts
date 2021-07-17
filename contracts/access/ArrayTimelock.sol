// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/governance/TimelockController.sol";

contract ArrayTimelock is TimelockController {
    constructor(uint256 _minDelay, address[] memory _proposers, address[] memory _executors)
    TimelockController(_minDelay, _proposers, _executors){

        // removing the admin role for the timelock contract guarantees that the minimum delay and the events
        // are being triggered for all functions for which it has the sole permission (ie changing proxy implementations,
        // yield, adding / removing roles

        renounceRole(TIMELOCK_ADMIN_ROLE, _msgSender());
    }
}


