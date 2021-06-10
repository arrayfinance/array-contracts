// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.4;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @notice As added security, the admin of this contract is the timelock controller, thus, any changes to roles
 * will have the minimum delay before enacted.
 **/

contract Roles is AccessControl {

    bytes32 public constant DEVELOPER = keccak256("DEVELOPER");
    bytes32 public constant DAO_MULTISIG = keccak256("DAO_MULTISIG");
    bytes32 public constant DEV_MULTISIG = keccak256("DEV_MULTISIG");
    bytes32 public constant TIMELOCK = keccak256("TIMELOCK");

    constructor(address _developer, address _daomsig, address _devmsig, address _timelock){

        _setupRole(DEVELOPER, _developer);
        _setupRole(DAO_MULTISIG, _daomsig);
        _setupRole(DEV_MULTISIG, _devmsig);
        _setupRole(TIMELOCK, _timelock);
        _setupRole(DEFAULT_ADMIN_ROLE, _timelock);
    }

}
