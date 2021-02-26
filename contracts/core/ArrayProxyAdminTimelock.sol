// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/governance/TimelockController.sol";

/** @title  Time lock for proxy admin contract.
    @dev    The address is the address of the proxy admin contract, used to upgrade individual proxies.
            Proposer role should be governance / DAO, while executor can be any EOA.
            Min delay 24hs or 1 day.
 */

abstract contract ArrayProxyAdminTimelock is TimelockController{
}
