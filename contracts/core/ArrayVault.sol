// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "openzeppelin-contracts/contracts/utils/Initializable.sol";

contract ArrayVault is Initializable {
    address public owner;

    function initialize(address _owner) initializer public {
        owner = _owner;
    }
}
