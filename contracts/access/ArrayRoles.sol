// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";

contract ArrayRoles is AccessControl {

    bytes32 public constant DEVELOPER = keccak256("DEVELOPER");
    bytes32 public constant DAO_MULTISIG = keccak256("DAO_MULTISIG");
    bytes32 public constant DEV_MULTISIG = keccak256("DEV_MULTISIG");
    address private constant devmultisig = 0x3c25c256E609f524bf8b35De7a517d5e883Ff81C;
    address private constant daomultisig = 0xB60eF661cEdC835836896191EDB87CC025EFd0B7;

    constructor () {

        _setupRole(DEFAULT_ADMIN_ROLE, daomultisig);
        _setupRole(DAO_MULTISIG, daomultisig);
        _setupRole(DEV_MULTISIG, devmultisig);
        _setupRole(DEVELOPER, msg.sender);
        _setRoleAdmin(DEVELOPER, DEV_MULTISIG);
    }
}
