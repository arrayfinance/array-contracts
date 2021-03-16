// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./BancorFormula.sol";

interface IChainLinkFeed {
    function latestAnswer() external view returns (int256);
}

/**
 * @title Bonding Curve
 * @dev Bonding curve contract based on Bacor formula
 * inspired by bancor protocol and simondlr
 * https://github.com/bancorprotocol/contracts
 * https://github.com/ConsenSys/curationmarkets/blob/master/CurationMarkets.sol
 */
contract BondingCurve is ArrayToken, BancorFormula, Ownable {
    /**
     * @dev Available balance of reserve token in contract
     */
    uint256 public poolBalance;
    IChainLinkFeed public constant FASTGAS = IChainLinkFeed(0x169E633A2D1E6c10dD91238Ba11c4A708dfEF37C);

    /*
     * @dev reserve ratio, represented in ppm, 1-1000000
     * 1/3 corresponds to y= multiple * x^2
     * 1/2 corresponds to y= multiple * x
     * 2/3 corresponds to y= multiple * x^1/2
     * multiple will depends on contract initialization,
     * specificallytotalAmount and poolBalance parameters
     * we might want to add an 'initialize' function that will allow
     * the owner to send ether to the contract and mint a given amount of tokens
    */
    uint32 public reserveRatio = 500000;

    uint256 public gasPrice = 0 wei; // maximum gas price for bancor transactions

    modifier validGasPrice() {
        require(
            tx.gasprice <= uint(FASTGAS.latestAnswer()),
            "Must send equal to or lower than maximum gas price to mitigate front running attacks."
        );
        _;
    }

    function buy() validGasPrice public {
    }

    function sell(uint256 sellAmount) validGasPrice public {
    }

}
