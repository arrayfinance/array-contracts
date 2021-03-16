pragma solidity ^0.8.0;

interface I_ERC20 {
    // TODO
}

interface I_BondingCurve{
    // TODO
}

contract Curve {

    address public DAO_MULTISIG_ADDR = 0xB60eF661cEdC835836896191EDB87CC025EFd0B7;
    address public DEV_MULTISIG_ADDR = 0x3c25c256E609f524bf8b35De7a517d5e883Ff81C;
	address public SMART_POOL = 0x0;
    address public VESTING_MULTISIG_ADDR = 0x0;  // TODO
    address public HARVEST_MULTISIG_ADDR = 0x0; // TODO

    uint256 private DEV_PCT_DAI = 5 * 10**16; // 5%
    uint256 private DEV_PCT_ARRAY = 2 * 10**17; // 20%
    uint256 private DAO_PCT_ARRAY = 5 * 10**16;  // 5%
    uint256 private PRECISION = 10**18;

    uint256 public MAX_ARRAY_SUPPLY = 100000 * PRECISION;

    // Represents the 700k DAI spent for initial 10k tokens
    uint256 private STARTING_DAI_BALANCE = 700000 * PRECISION;

    // Starting supply of 10k ARRAY
    uint256 private STARTING_ARRAY_MINTED = 10000 * PRECISION;

    // Keeps track of LP tokens
    uint256 public virtualBalance = STARTING_DAI_BALANCE;

    // Keeps track of supply minted for bonding curve
    uint256 public virtualSupply = STARTING_ARRAY_MINTED;

    // Keeps track of DAI for team multisig
    uint256 public devFundDaiBalance;

    // Keeps track of ARRAY for team multisig
    uint256 public devFundArrayBalance;

    // Keeps track of ARRAY for DAO multisig
    uint256 public daoArrayBalance;

    // Used to calculate bonding curve slope
    uint32 public reserveRatio; // TODO

    // Initial purchase of ARRAY from the CCO
    bool private initialized;

    address public owner;
    address public devFund;
    address public gov;
    I_ERC20 public ARRAY;
    I_ERC20 public DAI;
	I_ERC20 public LPTOKEN;
	I_ERC20 public WETH;
	I_ERC20 public RENBTC;
	I_ERC20 public WBTC;
    I_BondingCurve public CURVE;
    address[] public virtualLPTokens;

    mapping(address => uint256) public deposits;
    mapping(address => uint256) public purchases;

    event Buy(); // TODO
    event Burned(address sender, uint256 amount, uint256 withdrawal);
    event WithdrawDevFunds(address token, uint256 amount);
    event WithdrawDaoFunds(uint256 amount);

    constructor(
        address _owner,
        address _dai,
        address _arrayToken,
        address _curve,
		address _lpToken
    ) public {
        owner = _owner;
        DAI = I_ERC20(_dai);
        ARRAY = I_ERC20(_arrayToken);
		LPTOKEN = I_ERC20(_lpToken);
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


    function buy(uint256 amountDai) public nonReentrant {  // TODO: import nonReentrant from OZ
        require(initialized, "!initialized");
        require(amountDai > 0, "buy: cannot deposit 0 tokens");
        require(DAI.balanceOf(msg.sender) >= amountDai, "buy: cannot deposit more than user balance");

        // TODO: deposit DAI into smartpool
        require(DAI.transferFrom(msg.sender, address(this), amountDai));

        // TODO: return amount of smartpool LP tokens

        // Virtual balance - amount of LP tokens

        // Calculate quantity of ARRAY minted based on total DAI spent
        uint256 amountArrayTotal = CURVE.calculatePurchaseReturn(
            virtualSupply,
            virtualBalance,
            reserveRatio,
            amountDaiDeposited
        );

        // Only track 95% of dai deposited, as 5% goes to team
        uint256 amountDaiDeposited = amountDai * DEV_PCT_DAI / PRECISION;
        uint256 amountDaiDevFund = amountDai - amountDaiDeposited;

        // Only mint 95% of ARRAY total to account for 5% DAI dev fund
        uint256 amountArrayMinted = amountArrayTotal * (PRECISION - DEV_PCT_DAI);
        require(amountArrayMinted <= MAX_ARRAY_SUPPLY, "buy: amountArrayTotal > max supply");

        // 20% of total ARRAY sent to Array team vesting
        uint256 amountArrayDevFund = amountArrayTotal * DEV_PCT_ARRAY / PRECISION;

        // 5% of total ARRAY sent to DAO multisig
        uint256 amountArrayDao = amountArrayTotal * DAO_PCT_ARRAY / PRECISION;

        // Remaining ARRAY goes to buyer
        uint256 amountArrayBuyer = amountArrayMinted - amountArrayDevFund - amountArrayDao;
        
        // Update balances
        devFundDaiBalance = devFundDaiBalance + amountDaiDevFund;
        devFundArrayBalance = devFundArrayBalance + amountArrayDevFund;
        daoArrayBalance = daoArrayBalance + amountArrayDao;

        // Update virtual balance and supply
        virtualBalance = virtualBalance + amountDaiDeposited;
        virtualSupply = virtualSupply + amountArrayMinted;

        // Mint buyer's ARRAY to buyer
        ARRAY.mint(msg.sender, amountArrayBuyer);

        // Mint devFund's ARRAY to this contract for holding
        ARRAY.mint(address(this), amountArrayDevFund);

        emit Buy(); // TODO
    }

    function sell(uint256 amountArray, bool max) {

        if (max) {amountArray = ARRAY.balanceOf(msg.sender);}        

        
        // get curve contract balance of LPtoken

        
        // get total supply of array token, subtract amount burned

        
        // get % of burned supply

        
        // return burned supply % as LPtoken to user

        
        // update virtual balance and supply


        emit Burned(msg.sender, amountArraySeller, amountDai);
    }


    function withdrawDevFunds(address token, uint256 amount, bool max) returns (bool) {
        require(msg.sender == DEV_MULTISIG_ADDR, "withdrawDevFunds: msg.sender != DEV_MULTISIG_ADDR");
        require(token == address(ARRAY) || token == address(DAI), "withdrawDevFunds: token != DAI || ARRAY");

        if (token == address(ARRAY)) {
            require(amount <= devFundArrayBalance);
            if (max) {amount = devFundArrayBalance;}
            require(ARRAY.mint(VESTING_MULTISIG_ADDR, amount));
            devFundArrayBalance = devFundArrayBalance - amount;
        } else { // token == address(DAI)
            require(amount <= devFundDaiBalance);
            if (max) {amount = devFundDaiBalance;}
            require(DAI.transfer(DEV_MULTISIG_ADDR, amount));
            devFundDaiBalance = devFundDaiBalance - amount;
        }

        emit WithdrawDevFunds(token, amount);
    }

    function withdrawDaoFunds(uint256 amount, bool max) returns (bool) {
        require(
            msg.sender == DAO_MULTISIG_ADDR || msg.sender == HARVEST_ADDR,
            "withdrawDaoFunds: msg.sender != DAO_MULTISIG_ADDR || HARVEST_ADDR"
        );
        if (max) {amount = daoArrayBalance;}
        require(ARRAY.transfer(DAO_MULTISIG_ADDR, amount));
        daoArrayBalance = daoArrayBalance - amount;

        emit WithdrawDaoFunds(amount);
    }
    // TODO: make this callable only from harvest

    function isTokenInLP(address token) external view returns (bool) {
        // TODO
    }

    function isTokenInVirtualLP(address token) external view returns (bool) {
        for (uint i=0; i=virtualLPTokens.length; i++) {
            if (token == virtualLPTokens[i]) {
                return true;
            }
        }
        return false;
    }

    function getTokenIndexInVirtualLP(address token) external view returns (uint256) {
        require(isTokenInVirtualLP(token), "Token not in virtual LP");
        for (uint i=0; i=virtualLPTokens.length; i++) {
            if (token == virtualLPTokens[i]) {
                return i;
            }
        }
    }

    function addTokenToVirtualLP(address token) {
        require(msg.sender == gov, "msg.sender != gov");
        require(isTokenInLP(token), "Token not in Balancer LP");
        require(!tokenInVirtualLP(), "Token already added to virtual LP");

        virtualLPTokens.push(token);

        emit AddTokenToVirtualLP(token); // TODO
    }

    function removeTokenFromVirtualLP(address token) {
        require(msg.sender == gov, "msg.sender != gov");
        uint256 tokenIndex = getTokenIndexInVirtualLP(token);
        
        delete virtualLPTokens[tokenIndex];

        emit RemoveTokenFromVirtualLP(token); // TODO 
    }
}