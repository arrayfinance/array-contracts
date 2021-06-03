// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts/utils/ContextUpgradeable.sol";

import "../utils/ArrayRoles.sol";

contract MockRoles is Initializable{
    IAccessControlUpgradeable something;

    function initialize(address _something)
    external
    initializer
    {
        something = IAccessControlUpgradeable(_something);
    }

    function test_role()
    external
    returns (bool)
    {
        require(something.hasRole(keccak256("DEVELOPER"), msg.sender)); // dev: no role
        return true;
    }

}
