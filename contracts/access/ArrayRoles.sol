// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";

/**
 * @dev As added security, the admin of this contract is the timelock controller, thus, any changes will have the
 * minimum delay (24hs) before enacted.
 **/

contract ArrayRoles is AccessControl, Initializable {

    address public owner;
    // roles from least permissioned to most permissioned,

    // DEVELOPER is in charge of operational functions, also in case of emergency withdraw all funds from strategy to vault
    // but never make changes to how the funds are being handled
    bytes32 public constant DEVELOPER = keccak256("DEVELOPER");

    bytes32 public constant GOVERNANCE = keccak256("GOVERNANCE");
    bytes32 public constant DAO_MULTISIG = keccak256("DAO_MULTISIG");
    bytes32 public constant DEV_MULTISIG = keccak256("DEV_MULTISIG");

    // TIMELOCK can change the strategy for every vault and change implementations
    bytes32 public constant TIMELOCK = keccak256("TIMELOCK");

    constructor () {
        owner = msg.sender;
    }

    function initialize(address _developer, address _governance, address _timelock)
    public initializer
    {
        require(msg.sender == owner, "!owner");
        // set up roles
        _setupRole(DEFAULT_ADMIN_ROLE, _timelock);
        _setupRole(DEVELOPER, _developer);
        _setupRole(DAO_MULTISIG, address(0xB60eF661cEdC835836896191EDB87CC025EFd0B7));
        _setupRole(DEV_MULTISIG, address(0x3c25c256E609f524bf8b35De7a517d5e883Ff81C));
        _setupRole(GOVERNANCE, _governance);
        _setupRole(TIMELOCK, _timelock);
    }
}
