// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts-upgradeable/utils/StorageSlotUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

//interface IAccessControlStorage {
//    function onlyDev() external returns (bool);
//    function onlyDaoMsig() external;
//    function onlyDevMsig() external;
//    function onlyTimelock() external;
//}

contract AccessControlStorage is Initializable, UUPSUpgradeable, AccessControlUpgradeable {

    using StorageSlotUpgradeable for bytes32;

    bytes32 internal constant _DEVELOPER = 0x80b49ba303b5805ea0433f9071f6a1cb288f7ca4dbd9dc5ecc21bbc7e79ab651;
    bytes32 internal constant _DAOMSIG = 0x432d356d72775947833f89265afbbca5eec2962ae4b2091b38b20b78f4aea729;
    bytes32 internal constant _DEVMSIG = 0xe7900e67a3e93cc57b685a847308c5abe394968fa322f27d33b23d4bc61f8fed;
    bytes32 internal constant _TIMELOCK = 0x1a03d1622c87f0b21b8fb4f83e009dbe6fbb525f6d64b84523c04bdd287d0069;

//    modifier _onlyDev() {
//        _checkRole(getRoleSlot(_DEVELOPER), _msgSender());
//        _;
//    }
//
//    modifier _onlyDaoMsig() {
//        _checkRole(getRoleSlot(_DAOMSIG), _msgSender());
//        _;
//    }
//
//    modifier _onlyDevMsig() {
//        _checkRole(getRoleSlot(_DEVMSIG), _msgSender());
//        _;
//    }
//
//    modifier _onlyTimelock() {
//        _checkRole(getRoleSlot(_TIMELOCK), _msgSender());
//        _;
//    }

    function initialize(address _developer, address _daomsig, address _devmsig, address _timelock)
    public
    initializer
    {

        require(_DEVELOPER == bytes32(uint256(keccak256("eip1967.accesscontrol.storage.developer")) - 1), "!_DEVELOPER_SLOT");
        require(_DAOMSIG == bytes32(uint256(keccak256("eip1967.accesscontrol.storage.daomsig")) - 1), "!_DAOMSIG_SLOT");
        require(_DEVMSIG == bytes32(uint256(keccak256("eip1967.accesscontrol.storage.devmsig")) - 1), "!_DEVMSIG_SLOT");
        require(_TIMELOCK == bytes32(uint256(keccak256("eip1967.accesscontrol.storage.timelock")) - 1), "!_TIMELOCK_SLOT");

        _setRoleSlot(_DEVELOPER, keccak256("DEVELOPER"));
        _setRoleSlot(_DAOMSIG, keccak256("DAOMSIG"));
        _setRoleSlot(_DEVMSIG, keccak256("DEVMSIG"));
        _setRoleSlot(_TIMELOCK, keccak256("TIMELOCK"));

        __AccessControl_init();

        _setupRole(DEFAULT_ADMIN_ROLE, _timelock);
        _setupRole(getRoleSlot(_DEVELOPER), _developer);
        _setupRole(getRoleSlot(_DAOMSIG), _daomsig);
        _setupRole(getRoleSlot(_DEVMSIG), _devmsig);
        _setupRole(getRoleSlot(_TIMELOCK), _timelock);

    }


    function getRoleSlot(bytes32 slot)
    internal
    view
    returns (bytes32)
    {
        return slot.getBytes32Slot().value;

    }

    function _setRoleSlot(bytes32 slot, bytes32 value)
    private
    {
        slot.getBytes32Slot().value = value;
    }

    function _authorizeUpgrade(address newImplementation)
    internal
    override (UUPSUpgradeable)
    {}


    function onlyDev()
    public
    view
    returns (bool)
    {
        return hasRole(getRoleSlot(_DEVELOPER), tx.origin);
    }

//    function onlyDaoMsig()
//    external
//    _onlyDaoMsig
//    {}
//
//    function onlyDevMsig()
//    external
//    _onlyDevMsig
//    {}
//
//    function onlyTimelock()
//    external
//    _onlyTimelock
//    {}

}
