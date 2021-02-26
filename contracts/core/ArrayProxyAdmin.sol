// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/proxy/transparent/ProxyAdmin.sol";


/** @title  Admin contract for deployed proxies
    @dev    Once deployed, the owner needs to be set to the TimeLock contract, since all functions are to be
            called through the Timelock contract.
 */

contract ArrayProxyAdmin is ProxyAdmin {
}
