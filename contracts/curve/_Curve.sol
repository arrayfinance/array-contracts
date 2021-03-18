pragma solidity ^0.8.0;

interface I_ERC20 {
    function mint() ;
    function transferFrom() ;
    function transfer() ;
    function balanceOf();
}

interface I_BondingCurve {
    function calculatePurchaseReturn();
}

interface I_BalancerPoolV2 {
    function queryJoinGivenIn();
}

contract Curve {

    address public DAO_MULTISIG_ADDR = 0xB60eF661cEdC835836896191EDB87CC025EFd0B7;
    address public DEV_MULTISIG_ADDR = 0x3c25c256E609f524bf8b35De7a517d5e883Ff81C;
	address public BALANCERPOOL = 0x0;
    address public VESTING_MULTISIG_ADDR = 0x0;  // TODO
    address public HARVEST_MULTISIG_ADDR = 0x0; // TODO

    uint256 private DEV_PCT_LP = 5 * 10**16; // 5%
    uint256 private DEV_PCT_ARRAY = 2 * 10**17; // 20%
    uint256 private DAO_PCT_ARRAY = 5 * 10**16;  // 5%
    uint256 private PRECISION = 10**18;

    uint256 public MAX_ARRAY_SUPPLY = 100000 * PRECISION;

    // Represents the 700k DAI spent for initial 10k tokens
    uint256 private STARTING_DAI_BALANCE = 700000 * PRECISION;

    // Starting supply of 10k ARRAY
    uint256 private STARTING_ARRAY_MINTED = 10000 * PRECISION;

    // Keeps track of LP tokens
    // TODO: update this with LP balance from 
    uint256 public virtualBalance;

    // Keeps track of ARRAY minted for bonding curve
    uint256 public virtualSupply = STARTING_ARRAY_MINTED;

    // Keeps track of the max amount of ARRAY supply
    uint256 public maxSupply = 100000 * PRECISION;

    // Keeps track of DAI for team multisig
    uint256[] public devFundLPBalance;

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
	I_ERC20 public LPTOKEN;
    
    I_BondingCurve public CURVE;
    I_BalancerPoolV2 public BALANCERPOOL;
    
    address[] public virtualLPTokens;

    mapping(address => uint256) public deposits;
    mapping(address => uint256) public purchases;

    event Buy(); // TODO
    event Sell(); // TODO
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

        // Send LP tokens from governance to curve
        initialAmountLPToken = LPTOKEN.balanceOf(gov);
        require(LPTOKEN.transferFrom(gov, address(this), initialAmountLPToken), "Transfer failed");

        // Mint ARRAY to CCO
        ARRAY.mint(to, STARTING_ARRAY_MINTED);
        
        // 


        initialized = true;
    }


    function buy(address token, uint256 amount) public nonReentrant {  // TODO: import nonReentrant from OZ
        require(initialized, "!initialized");
        require(isTokenInLP(token), "Token not in LP");
        require(isTokenInVirtualLP(token), "Token not greenlisted");
        require(amount > 0, "buy: cannot deposit 0 tokens");

        // TODO: calculate amount of smartpool LP tokens
        uint256 amountLPTokenTotal = 0;

        // Calculate quantity of ARRAY minted based on total LP tokens
        uint256 amountArrayMinted = CURVE.calculatePurchaseReturn(
            virtualSupply,
            virtualBalance,
            reserveRatio,
            amountLPTokenTotal
        );

        // Only track 95% of LP deposited, as 5% goes to team
        uint256 amountLPTokenDeposited = amountLPToken * DEV_PCT_LP / PRECISION;
        uint256 amountLPTokenDevFund = amountLPToken - amountLPTokenDeposited;

        // Only mint 95% of ARRAY total to account for 5% DAI dev fund
        uint256 amountArrayMinted = amountArrayMinted * (PRECISION - DEV_PCT_LP);
        require(amountArrayMinted <= maxSupply, "buy: amountArrayMinted > max supply");

        // 20% of total ARRAY sent to Array team vesting
        uint256 amountArrayDevFund = amountArrayMinted * DEV_PCT_ARRAY / PRECISION;

        // 5% of total ARRAY sent to DAO multisig
        uint256 amountArrayDao = amountArrayMinted * DAO_PCT_ARRAY / PRECISION;

        // Remaining ARRAY goes to buyer
        uint256 amountArrayBuyer = amountArrayMinted - amountArrayDevFund - amountArrayDao;

        // TODO: deposit assets into smartpool
        require(LPTOKEN.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        
        // Mint devFund's ARRAY to this contract for holding
        ARRAY.mint(address(this), amountArrayDevFund);

        // Mint buyer's ARRAY to buyer
        ARRAY.mint(msg.sender, amountArrayBuyer);

        // Update balances (TODO?)
        devFundLPTokenBalance = devFundLPTokenBalance + amountLPTokenDevFund;
        devFundArrayBalance = devFundArrayBalance + amountArrayDevFund;
        daoArrayBalance = daoArrayBalance + amountArrayDao;

        // Update virtual balance and supply
        virtualBalance = virtualBalance + amountLPTokenDeposited;
        virtualSupply = virtualSupply + amountArrayMinted;

        emit Buy(); // TODO
    }

    function sell(uint256 amountArray, bool max) {

        if (max) {amountArray = ARRAY.balanceOf(msg.sender);}
        require(ARRAY.balanceOf(msg.sender) <= amountArray, "Cannot burn more than amount");

        // get curve contract balance of LPtoken
        uint256 curveLPTokenBalance = LPTOKEN.balanceOf(address(this));

        // get total supply of array token, subtract amount burned
        uint256 amountArrayAfterBurn = virtualSupply - amountArray;
        
        // get % of burned supply
        uint256 pctArrayBurned = amountArrayAfterBurn * PRECISION / virtualSupply;

        // calculate how much of the LP token the burner gets
        uint256 amountLPTokenReturned = pctArrayBurned * virtualBalance / PRECISION;

        // burn token TODO
        ARRAY.burn(msg.sender, amountArray);

        // send to burner
        require(LPTOKEN.transfer(msg.sender, amountLPTokenReturned), "Transfer failed");
        
        // update virtual balance and supply
        virtualBalance = virtualBalance - amountLPTokenReturned;
        virtualSupply = virtualSupply - amountArray;

        emit Sell();  // TODO
    }



    function withdrawDevFunds(address token, uint256 amount, bool max) returns (bool) {
        require(msg.sender == DEV_MULTISIG_ADDR, "withdrawDevFunds: msg.sender != DEV_MULTISIG_ADDR");

        if (token == address(ARRAY)) {
            require(amount <= devFundArrayBalance);
            if (max) {amount = devFundArrayBalance;}
            require(ARRAY.mint(VESTING_MULTISIG_ADDR, amount));
            devFundArrayBalance = devFundArrayBalance - amount;
        } else {

            require(amount <= devFundLPTokenBalance);
            if (max) {amount = devFundLPTokenBalance;}
            require(DAI.transfer(DEV_MULTISIG_ADDR, amount));
            devFundLPTokenBalance = devFundLPTokenBalance - amount;
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

    function addTokenToVirtualLP(address token) public {
        require(msg.sender == gov, "msg.sender != gov");
        require(isTokenInLP(token), "Token not in Balancer LP");
        require(!isTokenInVirtualLP(), "Token already added to virtual LP");

        virtualLPTokens.push(token);

        emit AddTokenToVirtualLP(token); // TODO
    }

    function removeTokenFromVirtualLP(address token) public {
        require(msg.sender == gov, "msg.sender != gov");
        uint256 tokenIndex = getTokenIndexInVirtualLP(token);
        
        delete virtualLPTokens[tokenIndex];

        emit RemoveTokenFromVirtualLP(token); // TODO 
    }
}