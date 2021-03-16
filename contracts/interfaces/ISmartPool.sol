// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

interface ISmartPool {

    function totalSupply() external view returns (uint);

    function joinswapExternAmountIn(
        address tokenIn,
        uint tokenAmountIn,
        uint minPoolAmountOut
    ) external returns (uint poolAmountOut);

    function exitswapPoolAmountIn(
        address tokenOut,
        uint poolAmountIn,
        uint minAmountOut
    ) external returns (uint tokenAmountOut);

}
