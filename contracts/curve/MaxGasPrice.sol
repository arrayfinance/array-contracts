// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

interface IChainLinkFeed {
    function latestAnswer() external view returns (int256);
}

contract MaxGasPrice {
    IChainLinkFeed public constant FASTGAS = IChainLinkFeed(0x169E633A2D1E6c10dD91238Ba11c4A708dfEF37C);

    modifier validGasPrice() {
        require(
            tx.gasprice <= uint(FASTGAS.latestAnswer()),
            "Must send equal to or lower than fast gas price to mitigate front running attacks."
        );
        _;
    }
}
