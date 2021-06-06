// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts/proxy/utils/Initializable.sol";

contract Mock is Initializable {
    address public something;

    function initialize(address _something)
    external
    initializer
    {
        something = _something;
    }

}
