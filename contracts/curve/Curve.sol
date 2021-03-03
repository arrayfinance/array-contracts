pragma solidity ^0.8.0;

interface I_ERC20 {
    // TODO
}

interface I_BondingCurve{
    // TODO
}

contract Curve {

    
    uint256 private DEV_PCT = 3 * 10**17; // 30%
    uint256 private PRECISION = 10**18;

    // Represents the 1MM DAI pledged
    uint256 private STARTING_DAI_BALANCE = 1000000 * PRECISION;

    // Starting supply of 10k ARRAY
    uint256 private STARTING_ARRAY_MINTED = 10000 * PRECISION;

    // Keeps track of supply sold for bonding curve
    uint256 public virtualSupply;

    // Used to calculate bonding curve slope
    uint32 public reserveRatio; // TODO

    // Initial purchase of ARRAY from the CCO
    bool private initialized;

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

    function initialize(address to) public {
        require(!initialized, "intialized");
        require(msg.sender == owner, "!owner");

        // Mint ARRAY to CCO
        ARRAY.mint(to, STARTING_ARRAY_MINTED);

        // Set virtual balance of supply to our 10k tokens
        virtualSupply = STARTING_ARRAY_MINTED;

        // Send 300k DAI to dev fund
        DAI.transfer(devFund, 300000 * PRECISION);

        initialized = true;
    }



    function buy(uint256 amountDai) public {
        require(amountDai > 0, "buy: cannot deposit 0 tokens");
        require(DAI.balanceOf(msg.sender) >= amountDai, "buy: cannot deposit more than user balance");
        
        require(DAI.transferFrom(msg.sender, address(this), amountDai), "buy: transferFrom failed");

        uint256 amountArrayBuyer = CURVE.calculatePurchaseReturn(param);

        // TODO: calculations for buyer / dev team



        // Update virtual balance of supply
        virtualSupply = virtualSupply + 

        
        deposits[msg.sender] = deposits[msg.sender] + amountDai;
        purchases[msg.sender] = purchases[msg.sender] + amountArrayBuyer;

        emit Minted(msg.sender, amountArrayBuyer, amountDai);
    }

    function sell(uint256 amountArray) {
        // TODO
    }

}