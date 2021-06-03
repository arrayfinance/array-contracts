// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

interface IChainLinkFeed {
    function latestAnswer() external view returns (int256);
}
