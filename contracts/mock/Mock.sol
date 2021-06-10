// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/StorageSlotUpgradeable.sol";

import "../access/RolesInit.sol";

contract Mock is Initializable, UUPSUpgradeable, OwnableUpgradeable, RolesInit {
//    bytes32 internal constant _ACCESS_CONTROL_SLOT = 0x2ebeb02267d1704e4bf8bcfb1b1d751fc2d2252186e82c21c4353a67bf297e64;
    string public something;


    function initialize(string memory _something, address _accessControl)
    external
    initializer
    {
        something = _something;
        RolesInit.initialize(_accessControl);
        __Ownable_init();
        __UUPSUpgradeable_init();
    }

//    function getACSlot()
//    internal
//    view
//    returns (address)
//    {
//        return _ACCESS_CONTROL_SLOT.getAddressSlot().value;
//
//    }
//
//    function _setACSlot(bytes32 slot, bytes32 value)
//    private
//    {
//        slot.getAddressSlot().value = value;
//    }

    function getImplementation()
    external
    view
    returns (address)
    {
        return _getImplementation();
    }

    function restricted()
    external
    view
    _onlyDev
    { }

    function _authorizeUpgrade(address)
    internal
    override
    onlyOwner()
    {}

//    function restrictedDev()
//    internal
//    {
//        AccessControlStorage(getACSlot()).onlyDev();
//    }
//

}
