// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";

/**
 * @notice PROXIED, CHANGING ORDER/TYPE OF STORAGE VARIABLES WILL BREAK THINGS IF IMPLEMENTING IN SAME PROXY

 * @dev As added security, the owner of this contract is the timelock controller, thus, any changes will have the
 * minimum delay (24hs) before enacted.
 **/

contract ArrayRoles is AccessControlUpgradeable {

    // roles from least permissioned to most permissioned,

    // DEVELOPER is in charge of operational functions, also in case of emergency withdraw all funds from strategy to vault
    // but never make changes to how the funds are being handled
    bytes32 public constant DEVELOPER = keccak256("DEVELOPER");

    // GOVENRANCE likely be removed before deployment
    bytes32 public constant GOVERNANCE = keccak256("GOVERNANCE");

    // VAULT_TIMELOCK can change the proxy implementation (ie vaults)
    bytes32 public constant VAULT_TIMELOCK = keccak256("VAULT_TIMELOCK");

    // STRATEGY_TIMELOCK can change the strategy for every vault
    bytes32 public constant STRATEGY_TIMELOCK = keccak256("VAULT_TIMELOCK");

    function initialize(address _developer, address _governance, address _timelock)
    public
    initializer
    {

        // set up roles
        __AccessControl_init();

        _setupRole(DEFAULT_ADMIN_ROLE, _timelock);

        _setupRole(DEVELOPER, _developer);
        _setupRole(GOVERNANCE, _governance);
        _setupRole(VAULT_TIMELOCK, _timelock);
        _setupRole(STRATEGY_TIMELOCK, _timelock);

    }
}
