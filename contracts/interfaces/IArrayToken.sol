// SPDX-License-Identifier: MIT


pragma solidity ^0.8.0;

interface IArrayToken {
    function mint(address to, uint256 amount) external;
    function burn(address to, uint256 amount) external;
    function totalSupply() external view returns (uint256);
}
