// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

interface ISmartPool {

    function totalSupply() external view returns (uint);

    function transfer(address dst, uint amt) external returns (bool);

    function transferFrom(
        address src, address dst, uint amt
    ) external returns (bool);

    function bPool() external view returns (address);

    function joinswapExternAmountIn(
        address tokenIn,
        uint tokenAmountIn,
        uint minPoolAmountOut
    ) external returns (uint poolAmountOut);
}
