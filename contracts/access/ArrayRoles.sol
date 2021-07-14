// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.4;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @dev As added security, the admin of this contract is the timelock controller, thus, any changes will have the
 * minimum delay (24hs) before enacted.
 **/

contract ArrayRoles is AccessControl {

    // roles from least permissioned to most permissioned,

    // DEVELOPER is in charge of operational functions, also in case of emergency withdraw all funds from strategy to vault
    // but never make changes to how the funds are being handled

    bytes32 public constant DEVELOPER = keccak256("DEVELOPER");
    bytes32 public constant DAO_MULTISIG = keccak256("DAO_MULTISIG");
    bytes32 public constant DEV_MULTISIG = keccak256("DEV_MULTISIG");

    // TIMELOCK can change the strategy for every vault and change implementations
    bytes32 public constant TIMELOCK = keccak256("TIMELOCK");

    constructor (address _developer, address _timelock) {

        _setupRole(DEFAULT_ADMIN_ROLE, _timelock);
        _setupRole(DEVELOPER, _developer);
        _setupRole(TIMELOCK, _timelock);
        _setupRole(DAO_MULTISIG, address(0xB60eF661cEdC835836896191EDB87CC025EFd0B7));
        _setupRole(DEV_MULTISIG, address(0x3c25c256E609f524bf8b35De7a517d5e883Ff81C));

    }
}
