// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "../../node_modules/@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "../../node_modules/@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "../../node_modules/@openzeppelin/contracts-upgradeable/utils/ContextUpgradeable.sol";

import "../access/ArrayRoles.sol";

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
