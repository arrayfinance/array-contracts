pragma solidity ^0.8.0;

interface I_ERC20 {
    // TODO
}

interface I_BondingCurve{
    // TODO
}

contract Curve {

    uint256 public DEV_PCT = 3 * 10**17; // 30%
    uint256 public PRECISION = 10**18;
    uint32 public reserveRatio; // TODO

    // To represent the 1MM DAI pledged
    uint256 public virtualBalance = 1000000 * PRECISION;

    // To represent the starting supply of 10k ARRAY
    uint256 public virtualSupply = 10000 * PRECISION;

    address public owner;
    address public devFund;
    I_ERC20 public ARRAY;
    I_ERC20 public DAI;
    I_BondingCurve public CURVE;

    mapping(address => uint256) public deposits;
    mapping(address => uint256) public purchases;

    event Minted(address sender, uint256 amount, uint256 deposit);
    event Burned(address sender, uint256 amount, uint256 deposit);

    constructor(
        address _owner,
        address _devFund,
        address _dai,
        address _arrayToken,
        address _curve
    ) public {
        owner = _owner;
        devFund = _devFund;
        DAI = I_ERC20(_dai);
        ARRAY = I_ERC20(_arrayToken);
        CURVE = I_BondingCurve(_curve);

        buy(virtualBalance);
    }

    function buy(uint256 amountDai) {
        require(amountDai > 0, "buy: cannot deposit 0 tokens");
        require(DAI.balanceOf(msg.sender) >= amountDai, "buy: cannot deposit more than user balance");
        
        require(DAI.transferFrom(msg.sender, address(this), amountDai), "buy: transferFrom failed");

        // TODO
        uint256 amountArray = CURVE.calculatePurchaseReturn(param);

        emit Minted(msg.sender, amountArray, amountDai);
    }

    function sell(uint256 amountArray) {
        // TODO
    }

}