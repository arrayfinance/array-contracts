pragma solidity ^0.8.0;

interface I_ERC20 {
    // TODO
}

interface I_BondingCurve{
    // TODO
}

contract Curve {

    uint256 private DEV_PCT_DAI = 10**17; // 10%
    uint256 private DEV_PCT_ARRAY = 2 * 10**17; // 20%
    uint256 private BUYER_PCT_ARRAY = 7 * 10**17; // 70%
    uint256 private PRECISION = 10**18;

    // Represents the 700k DAI spent for initial 10k tokens
    uint256 private STARTING_DAI_BALANCE = 700000 * PRECISION;

    // Starting supply of 10k ARRAY
    uint256 private STARTING_ARRAY_MINTED = 10000 * PRECISION;

    // Keeps track of DAI deposited
    uint256 public virtualBalance = STARTING_DAI_BALANCE;

    // Keeps track of DAI for team
    uint256 public devFundDaiBalance;

    // Keeps track of ARRAY for team
    uint256 public devFundArrayBalance;

    // Keeps track of supply minted for bonding curve
    uint256 public virtualSupply = STARTING_ARRAY_MINTED;

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
    event Burned(address sender, uint256 amount, uint256 withdrawal);

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
        // TODO
        require(!initialized, "intialized");
        require(msg.sender == owner, "!owner");

        // Mint ARRAY to CCO
        ARRAY.mint(to, STARTING_ARRAY_MINTED);

        initialized = true;
    }


    function buy(uint256 amountDai) public {
        require(initialized, "!initialized");
        require(amountDai > 0, "buy: cannot deposit 0 tokens");
        require(DAI.balanceOf(msg.sender) >= amountDai, "buy: cannot deposit more than user balance");
        require(DAI.transferFrom(msg.sender, address(this), amountDai));
        
        // 10% DAI allocated for dev team
        uint256 amountDaiDevFund = amountDai * DEV_PCT_DAI / PRECISION;
        devFundDaiBalance = devFundDaiBalance + amountDaiDevFund;
        
        // uint256 amountDaiCollateral = amountDai - amountDaiDevFund;

        uint256 amountArrayTotal = CURVE.calculatePurchaseReturn(
            virtualSupply,
            virtualBalance,
            reserveRatio,
            amountDai
        );

        // 20% ARRAY sent to dev team
        // Since we're only buying ARRAY with 90% DAI deposited,
        // Send 2/9 of array minted
        uint256 amountArrayDevFund = amountArrayTotal * 2 / ; // TODO: remove hardcoded numbers

        // Remaining 70% ARRAY sent to buyer, or 7/9 of ARRAY
        uint256 amountArrayBuyer = amountArrayTotal - amountArrayDevFund;

        // Update virtual balance and supply
        virtualBalance = virtualBalance + amountDaiCollateral;
        virtualSupply = virtualSupply + amountArrayTotal;

        // TODO: only track 70% of deposit?
        deposits[msg.sender] = deposits[msg.sender] + amountDai;
        purchases[msg.sender] = purchases[msg.sender] + amountArrayBuyer;

        ARRAY.mint(devFund, amountArrayDevFund);
        ARRAY.mint(msg.sender, amountArrayBuyer);

        emit Minted(msg.sender, amountArrayBuyer, amountDai);
    }

    function sell(uint256 amountArray, bool max) {

        if (max) {amountArray = ARRAY.balanceOf(msg.sender);}        



        emit Burned(msg.sender, amountArraySeller, amountDai);
    }

}