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

    uint256 public MAX_ARRAY_SUPPLY = 100000 * PRECISION;

    // Represents the 700k DAI spent for initial 10k tokens
    uint256 private STARTING_DAI_BALANCE = 700000 * PRECISION;

    // Starting supply of 10k ARRAY
    uint256 private STARTING_ARRAY_MINTED = 10000 * PRECISION;

    // Keeps track of DAI deposited
    uint256 public virtualBalance = STARTING_DAI_BALANCE;

    // Keeps track of supply minted for bonding curve
    uint256 public virtualSupply = STARTING_ARRAY_MINTED;

    // Keeps track of DAI for team
    uint256 public devFundDaiBalance;

    // Keeps track of ARRAY for team
    uint256 public devFundArrayBalance;

    // Used to calculate bonding curve slope
    uint32 public reserveRatio; // TODO

    // Initial purchase of ARRAY from the CCO
    bool private initialized;

    address public owner;
    address public devFund;
    address public gov;
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
        
        uint256 amountArrayTotal = CURVE.calculatePurchaseReturn(
            virtualSupply,
            virtualBalance,
            reserveRatio,
            amountDai
        );
        require(amountArrayTotal <= MAX_ARRAY_SUPPLY, "buy: amountArrayTotal > max supply");

        // Only track 90% of dai deposited, as 10% goes to team
        uint256 amountDaiDeposited = amountDai * 9 / 10;

        // Only mint 90% of ARRAY
        uint256 amountArrayMinted = amountArrayTotal * 9 / 10;  // TODO: hardcoding

        // 70% of ARRAY minted sent to dev team
        uint256 amountArrayBuyer = amountArrayTotal * 7 / 9;
        
        // Update dev fund balances
        uint256 amountDaiDevFund = amountDai - amountDaiDeposited;
        uint256 amountArrayDevFund = amountArrayMinted - amountArrayBuyer;
        devFundDaiBalance = devFundDaiBalance + amountDaiDevFund;
        devFundArrayBalance = devFundArrayBalance + amountArrayDevFund;

        // Update virtual balance and supply
        virtualBalance = virtualBalance + amountDaiDeposited;
        virtualSupply = virtualSupply + amountArrayTotal;

        // Update mappings of deposits / purchases
        deposits[msg.sender] = deposits[msg.sender] + amountDaiDeposited;
        purchases[msg.sender] = purchases[msg.sender] + amountArrayBuyer;

        // Send array to buyer
        ARRAY.mint(msg.sender, amountArrayBuyer);

        emit Minted(msg.sender, amountArrayBuyer, amountDai);
    }

    function sell(uint256 amountArray, bool max) {

        if (max) {amountArray = ARRAY.balanceOf(msg.sender);}        

        emit Burned(msg.sender, amountArraySeller, amountDai);
    }


    function withdrawDevFunds(address _token, uint256 amount, bool max) returns (bool) {
        require(msg.sender == gov, "withdrawDevFunds: !gov"); // TODO: gov address
        require(_token == address(ARRAY) || _token == address(DAI), "withdrawDevFunds: not DAI or ARRAY");

        if (_token == address(ARRAY)) {
            require(amount <= devFundArrayBalance);
            if (max) {amount = devFundArrayBalance;}
            require(ARRAY.mint(devFund, amount));
            devFundArrayBalance = devFundArrayBalance - amount;
        } else { // _token == address(DAI)
            require(amount <= devFundDaiBalance);
            if (max) {amount = devFundDaiBalance;}
            require(DAI.transfer(devFund, amount));
            devFundDaiBalance = devFundDaiBalance - amount;
        }
    }

}