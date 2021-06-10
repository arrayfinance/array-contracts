// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

contract MockExtended is Initializable, UUPSUpgradeable, OwnableUpgradeable{

    string public something;
    string public something_else; // this needs to be added after the previous variable or we'll have a clash

    function initialize(string memory _something)
    external
    initializer
    {
        something = _something;
        __Ownable_init();
        __UUPSUpgradeable_init();
    }

    function extend(string memory _something_else)
    public
    onlyOwner()
    {

        something_else = _something_else;
    }

    function getImplementation()
    external
    view
    returns (address)
    {
        return _getImplementation();
    }

    function _authorizeUpgrade(address)
    internal
    override
    onlyOwner()
    {}

}
