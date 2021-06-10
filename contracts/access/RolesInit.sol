// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/StorageSlotUpgradeable.sol";

import "../access/ArrayRolesStorage.sol";


contract RolesInit is Initializable {
    using StorageSlotUpgradeable for bytes32;

    bytes32 internal constant _ACCESS_CONTROL_SLOT = 0x2ebeb02267d1704e4bf8bcfb1b1d751fc2d2252186e82c21c4353a67bf297e64;

    modifier _onlyDev() {
        require(AccessControlStorage(getACSlot()).onlyDev(), "!DEV");
        _;
    }

    constructor() {
        require(_ACCESS_CONTROL_SLOT == bytes32(uint256(keccak256("eip1967.accesscontrolInit.storage")) - 1), "!_ACCESS_CONTROL_INIT");
    }

    function initialize(address _acstore) public initializer {
        require(_ACCESS_CONTROL_SLOT == bytes32(uint256(keccak256("eip1967.accesscontrolInit.storage")) - 1), "!_ACCESS_CONTROL_INIT");
        _setACSlot(_ACCESS_CONTROL_SLOT, _acstore);
    }

    function _setACSlot(bytes32 slot, address value)
    private
    {
        slot.getAddressSlot().value = value;
    }

    function getACSlot()
    internal
    view
    returns (address)
    {
        return _ACCESS_CONTROL_SLOT.getAddressSlot().value;

    }

}
