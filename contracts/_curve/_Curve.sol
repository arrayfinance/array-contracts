// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;


import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

interface I_ERC20 {
    function mint(address _to, uint256 amount) external;
    function burn(address _from, uint256 amount) external;
    function transferFrom(address _from, address _to, uint256 _value) external returns (bool success);
    function transfer(address _to, uint256 _value) external returns (bool success);
    function balanceOf(address _owner) external view returns (uint256 balance);
}

interface I_BondingCurve {
    function purchaseTargetAmount(uint256 _supply, uint256 _reserveBalance, uint32 _reserveWeight, uint256 _amount)
    external view returns (uint256);
}

interface I_SmartPool{

    function isPublicSwap() external view returns (bool);
    function isFinalized() external view returns (bool);
    function isBound(address t) external view returns (bool);
    function getNumTokens() external view returns (uint);
    function getCurrentTokens() external view returns (address[] memory tokens);
    function getFinalTokens() external view returns (address[] memory tokens);
    function getDenormalizedWeight(address token) external view returns (uint);
    function getTotalDenormalizedWeight() external view returns (uint);
    function getNormalizedWeight(address token) external view returns (uint);
    function getBalance(address token) external view returns (uint);
    function getSwapFee() external view returns (uint);
    function getController() external view returns (address);

    function setSwapFee(uint swapFee) external;
    function setController(address manager) external;
    function setPublicSwap(bool public_) external;
    function finalize() external;
    function bind(address token, uint balance, uint denorm) external;
    function rebind(address token, uint balance, uint denorm) external;
    function unbind(address token) external;
    function gulp(address token) external;

    function getSpotPrice(address tokenIn, address tokenOut) external view returns (uint spotPrice);
    function getSpotPriceSansFee(address tokenIn, address tokenOut) external view returns (uint spotPrice);

    function joinPool(uint poolAmountOut, uint[] calldata maxAmountsIn) external;
    function exitPool(uint poolAmountIn, uint[] calldata minAmountsOut) external;

    function swapExactAmountIn(
        address tokenIn,
        uint tokenAmountIn,
        address tokenOut,
        uint minAmountOut,
        uint maxPrice
    ) external returns (uint tokenAmountOut, uint spotPriceAfter);

    function swapExactAmountOut(
        address tokenIn,
        uint maxAmountIn,
        address tokenOut,
        uint tokenAmountOut,
        uint maxPrice
    ) external returns (uint tokenAmountIn, uint spotPriceAfter);

    function joinswapExternAmountIn(
        address tokenIn,
        uint tokenAmountIn,
        uint minPoolAmountOut
    ) external returns (uint poolAmountOut);

    function joinswapPoolAmountOut(
        address tokenIn,
        uint poolAmountOut,
        uint maxAmountIn
    ) external returns (uint tokenAmountIn);

    function exitswapPoolAmountIn(
        address tokenOut,
        uint poolAmountIn,
        uint minAmountOut
    ) external returns (uint tokenAmountOut);

    function exitswapExternAmountOut(
        address tokenOut,
        uint tokenAmountOut,
        uint maxPoolAmountIn
    ) external returns (uint poolAmountIn);

    function totalSupply() external view returns (uint);
    function balanceOf(address whom) external view returns (uint);
    function allowance(address src, address dst) external view returns (uint);

    function approve(address dst, uint amt) external returns (bool);
    function transfer(address dst, uint amt) external returns (bool);
    function transferFrom(
        address src, address dst, uint amt
    ) external returns (bool);

    function calcSpotPrice(
        uint tokenBalanceIn,
        uint tokenWeightIn,
        uint tokenBalanceOut,
        uint tokenWeightOut,
        uint swapFee
    ) external pure returns (uint spotPrice);

    function calcOutGivenIn(
        uint tokenBalanceIn,
        uint tokenWeightIn,
        uint tokenBalanceOut,
        uint tokenWeightOut,
        uint tokenAmountIn,
        uint swapFee
    ) external pure returns (uint tokenAmountOut);

    function calcInGivenOut(
        uint tokenBalanceIn,
        uint tokenWeightIn,
        uint tokenBalanceOut,
        uint tokenWeightOut,
        uint tokenAmountOut,
        uint swapFee
    ) external pure returns (uint tokenAmountIn);

    function calcPoolOutGivenSingleIn(
        uint tokenBalanceIn,
        uint tokenWeightIn,
        uint poolSupply,
        uint totalWeight,
        uint tokenAmountIn,
        uint swapFee
    ) external pure returns (uint poolAmountOut);

    function calcSingleInGivenPoolOut(
        uint tokenBalanceIn,
        uint tokenWeightIn,
        uint poolSupply,
        uint totalWeight,
        uint poolAmountOut,
        uint swapFee
    ) external pure returns (uint tokenAmountIn);


    function calcSingleOutGivenPoolIn(
        uint tokenBalanceOut,
        uint tokenWeightOut,
        uint poolSupply,
        uint totalWeight,
        uint poolAmountIn,
        uint swapFee
    ) external pure returns (uint tokenAmountOut);

    function calcPoolInGivenSingleOut(
        uint tokenBalanceOut,
        uint tokenWeightOut,
        uint poolSupply,
        uint totalWeight,
        uint tokenAmountOut,
        uint swapFee
    ) external pure returns (uint poolAmountIn);

}

contract Curve is ReentrancyGuard {

//    address public DAO_MULTISIG_ADDR = 0xB60eF661cEdC835836896191EDB87CC025EFd0B7;
//    address public DEV_MULTISIG_ADDR = 0x3c25c256E609f524bf8b35De7a517d5e883Ff81C;
//    address public VESTING_MULTISIG_ADDR = address(0);  // TODO
//    address public HARVEST_MULTISIG_ADDR = address(0); // TODO
//
//    uint256 private DEV_PCT_LP = 5 * 10**16; // 5%
//    uint256 private DEV_PCT_ARRAY = 2 * 10**17; // 20%
//    uint256 private DAO_PCT_ARRAY = 5 * 10**16;  // 5%
    uint256 private PRECISION = 10**18;
//
//    uint256 public m = 10**12;  // 1/1,000,000 (used for y = mx in _curve)

    uint256 public MAX_ARRAY_SUPPLY = 100000 * PRECISION;

    // Represents the 700k DAI spent for initial 10k tokens
    uint256 private STARTING_DAI_BALANCE = 700000 * PRECISION;

    // Starting supply of 10k ARRAY
    uint256 private STARTING_ARRAY_MINTED = 10000 * PRECISION;

    // Keeps track of LP tokens
    uint256 public virtualBalance;

    // Keeps track of ARRAY minted for bonding _curve
    uint256 public virtualSupply;

    // Keeps track of the max amount of ARRAY supply
    uint256 public maxSupply = 100000 * PRECISION;

    // @TODO Why an array?? (GISMAR)
    // Keeps track of DAI for team multisig
//    uint256 public devFundLPBalance;

    // Keeps track of ARRAY for team multisig
//    uint256 public devFundArrayBalance;

    // Keeps track of ARRAY for DAO multisig
//    uint256 public daoArrayBalance;

    // Used to calculate bonding _curve slope
    // Returns same result as x^2
    uint32 public reserveRatio = 333333; // symbolizes 1/3, based on bancor's max of 1/1,000,000

    // Initial purchase of ARRAY from the CCO
    bool private initialized;

    address public owner;
    address public devFund;
    address public gov;

    address[] public virtualLPTokens;

    I_ERC20 public DAI = I_ERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);
    I_ERC20 public ARRAY;
    I_SmartPool public SP_TOKEN;

//    mapping(address => uint256) public deposits;
//    mapping(address => uint256) public purchases;

    event Buy(
        address from,
        address token,
        uint256 amount,
        uint256 amountLPTokenDeposited,
        uint256 amountArrayMinted
    );

    event Sell(address from, uint256 amountArray, uint256 amountLPTokenReturned);
    event WithdrawDevFunds(address token, uint256 amount);
    event WithdrawDaoFunds(uint256 amount);

    constructor(
        address _owner,
        address _arrayToken,
        address _curve,
        address _smartPool
    ) {
        owner = _owner;
        ARRAY = I_ERC20(_arrayToken);
        CURVE = I_BondingCurve(_curve);
        SP_TOKEN = I_SmartPool(_smartPool);
    }

    function initialize(address to) public {
        uint256 initialAmountLPToken;

        require(!initialized, "intialized");
        require(msg.sender == owner, "!owner");

        // Send LP tokens from governance to _curve
        initialAmountLPToken = SP_TOKEN.balanceOf(address(this));
        require(SP_TOKEN.transferFrom(gov, address(this), initialAmountLPToken), "Transfer failed");

        // Mint ARRAY to CCO
        ARRAY.mint(DAO_MULTISIG_ADDR, STARTING_ARRAY_MINTED);
        
        // Set virtual balance and supply
        virtualBalance = initialAmountLPToken;
        virtualSupply = STARTING_ARRAY_MINTED;
        initialized = true;
    }

//    function isTokenInLP(address token) external view returns (bool) {
//        address[] memory lpTokens = SP_TOKEN.getCurrentTokens();
//        for (uint i=0; i <= lpTokens.length; i++) {
//            if (token == lpTokens[i]) {
//                return true;
//            }
//        }
//        return false;
//    }


    function buy(address token, uint256 amount) public nonReentrant {
        require(initialized, "!initialized");
//        require(this.isTokenInLP(token), "Token not in LP");
//        require(this.isTokenInVirtualLP(token), "Token not greenlisted");
        require(amount > 0, "buy: cannot deposit 0 tokens");

        uint256 amountArrayReturned = calculateArrayGivenTokenAndAmount(token, amount);

//         @TODO (GISMAR)
        // Only track 95% of LP deposited, as 5% goes to team
//        uint256 amountLPTokenDeposited = amountArrayReturned * DEV_PCT_LP / PRECISION;
//        uint256 amountLPTokenDevFund = amountArrayReturned - amountLPTokenDeposited;

        // Only mint 95% of ARRAY total to account for 5% LP dev fund
//        uint256 amountArrayMinted = amountArrayReturned * (PRECISION - DEV_PCT_LP);
//        require(amountArrayMinted <= maxSupply, "buy: amountArrayMinted > max supply");

        // 20% of total ARRAY sent to Array team vesting
//        uint256 amountArrayDevFund = amountArrayMinted * DEV_PCT_ARRAY / PRECISION;

        // 5% of total ARRAY sent to DAO multisig
//        uint256 amountArrayDao = amountArrayMinted * DAO_PCT_ARRAY / PRECISION;
        // Remaining ARRAY goes to buyer

//        uint256 amountArrayBuyer = amountArrayMinted - amountArrayDevFund - amountArrayDao;

        // Deposit assets into smartpool (TODO: validate)
        SP_TOKEN.joinswapExternAmountIn(token, amount, 0);
        
        // Mint devFund's ARRAY to this contract for holding
//        ARRAY.mint(address(this), amountArrayDevFund);

        // Mint buyer's ARRAY to buyer
//        ARRAY.mint(msg.sender, amountArrayBuyer);

        // Update balances (TODO?)
//        devFundLPBalance = devFundLPBalance + amountLPTokenDevFund;
//        devFundArrayBalance = devFundArrayBalance + amountArrayDevFund;
//        daoArrayBalance = daoArrayBalance + amountArrayDao;

        // Update virtual balance and supply
//        virtualBalance = virtualBalance + amountLPTokenDeposited;
//        virtualSupply = virtualSupply + amountArrayMinted;
    }



// @TODO What's this?
//
//    // TODO: make this callable only from harvest
//    function withdrawDaoFunds(uint256 amount, bool max) external returns (bool) {
//        require(
//            msg.sender == DAO_MULTISIG_ADDR || msg.sender == HARVEST_MULTISIG_ADDR,
//            "withdrawDaoFunds: msg.sender != DAO_MULTISIG_ADDR || HARVEST_ADDR"
//        );
//        if (max) {amount = daoArrayBalance;}
//        require(ARRAY.transfer(DAO_MULTISIG_ADDR, amount));
//        daoArrayBalance = daoArrayBalance - amount;
//        return True;
//
//    emit Buy(msg.sender, token, amount, amountLPTokenDeposited, amountArrayMinted);
//    }

    function sell(uint256 amountArray, bool max) external {

        if (max) {amountArray = ARRAY.balanceOf(msg.sender);}
        require(ARRAY.balanceOf(msg.sender) <= amountArray, "Cannot burn more than amount");

        // get _curve contract balance of LPtoken
        uint256 curveLPTokenBalance = SP_TOKEN.balanceOf(address(this));

        // get total supply of array token, subtract amount burned
        uint256 amountArrayAfterBurn = virtualSupply - amountArray;
        
        // get % of burned supply
        uint256 pctArrayBurned = amountArrayAfterBurn * PRECISION / virtualSupply;

        // calculate how much of the LP token the burner gets
        uint256 amountLPTokenReturned = pctArrayBurned * virtualBalance / PRECISION;

        // burn token
        ARRAY.burn(msg.sender, amountArray);

        // send to burner
        require(SP_TOKEN.transfer(msg.sender, amountLPTokenReturned), "Transfer failed");
        
        // update virtual balance and supply
        virtualBalance = virtualBalance - amountLPTokenReturned;
        virtualSupply = virtualSupply - amountArray;

        emit Sell(msg.sender, amountArray, amountLPTokenReturned);
    }


    function withdrawDevFunds(address token, uint256 amount, bool max) external returns (bool) {
        bool success = false;

        require(msg.sender == DEV_MULTISIG_ADDR, "withdrawDevFunds: msg.sender != DEV_MULTISIG_ADDR");


        if (token == address(ARRAY)) {
            require(amount <= devFundArrayBalance);
            if (max) {amount = devFundArrayBalance;}
//            require(ARRAY.mint(VESTING_MULTISIG_ADDR, amount)); // @TODO this doesn't return a bool.
            devFundArrayBalance = devFundArrayBalance - amount;
            success = true;

        } else {

            require(amount <= devFundLPBalance);
            if (max) {amount = devFundLPBalance;}
            require(DAI.transfer(DEV_MULTISIG_ADDR, amount));
            devFundLPBalance = devFundLPBalance - amount;
            success = true;
        }

        emit WithdrawDevFunds(token, amount);
        emit WithdrawDaoFunds(amount);

        return success;

    }


    function calculateArrayGivenTokenAndAmount(
        address token, uint256 amount

    ) public returns (uint256 amountArrayToMintNormalized) {
        // Calculate amount of smartpool LP tokens returned
        uint256 amountLPTokenTotal = SP_TOKEN.joinswapExternAmountIn(token, amount, 0);

        // Calculate quantity of ARRAY minted based on total LP tokens (Does not account for M)
        uint256 amountArrayToMint = CURVE.purchaseTargetAmount(
            virtualSupply,
            virtualBalance,
            reserveRatio,
            amountLPTokenTotal
        );

    }



//    function isTokenInVirtualLP(address token) external view returns (bool) {
//        for (uint i=0; i<=virtualLPTokens.length; i++) {
//            if (token == virtualLPTokens[i]) {
//                return true;
//            }
//        }
//        return false;
//    }

//    function getTokenIndexInVirtualLP(address token) external view returns (uint256) {
//        require(this.isTokenInVirtualLP(token), "Token not in virtual LP");
//        for (uint i=0; i<=virtualLPTokens.length; i++) {
//            if (token == virtualLPTokens[i]) {
//                return i;
//            }
//        }
//    }

//    function addTokenToVirtualLP(address token) public {
//        require(msg.sender == gov, "msg.sender != gov");
//        require(this.isTokenInLP(token), "Token not in Balancer LP");
//        require(!this.isTokenInVirtualLP(token), "Token already added to virtual LP");
//
//        virtualLPTokens.push(token);
//        emit addTokenToVirtualLP(token); // TODO
//    }

//    function removeTokenFromVirtualLP(address token) public {
//        require(msg.sender == gov, "msg.sender != gov");
//        uint256 tokenIndex = this.getTokenIndexInVirtualLP(token);
//
//        delete virtualLPTokens[tokenIndex];

 //       emit removeTokenFromVirtualLP(token); // TODO
    }
//}
