// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/governance/TimelockController.sol";

contract ArrayTimelock is TimelockController {
    constructor(uint256 _minDelay, address[] memory _proposers, address[] memory _executors)
    TimelockController(_minDelay, _proposers, _executors){
        address governance = _proposers[0];
        grantRole(TIMELOCK_ADMIN_ROLE, governance);
        renounceRole(TIMELOCK_ADMIN_ROLE, _msgSender());
    }
}


