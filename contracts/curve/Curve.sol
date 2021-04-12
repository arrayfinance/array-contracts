// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


interface I_ARRAY is IERC20 {
    function mint(address to, uint256 amount) external;

    function burn(address from, uint256 amount) external;
}

interface IChainLinkFeed {
    function latestAnswer() external view returns (int256);
}

interface I_BancorFormula {
    function calculatePurchaseReturn(uint256 _supply, uint256 _reserveBalance, uint32 _reserveWeight, uint256 _amount)
    external view returns (uint256);

    function calculateSaleReturn(uint256 _supply, uint256 _reserveBalance, uint32 _reserveWeight, uint256 _amount)
    external view returns (uint256);

}

interface I_CRP {
    function totalSupply() external view returns (uint);

    function transfer(address dst, uint amt) external returns (bool);

    function transferFrom(
        address src, address dst, uint amt
    ) external returns (bool);

    function bPool() external view returns (address);

    function joinswapExternAmountIn(
        address tokenIn,
        uint tokenAmountIn,
        uint minPoolAmountOut
    ) external returns (uint poolAmountOut);
}

interface I_BPool {

    function MAX_IN_RATIO() external view returns (uint);

    function getCurrentTokens() external view returns (address[] memory tokens);

    function getDenormalizedWeight(address token) external view returns (uint);

    function getTotalDenormalizedWeight() external view returns (uint);

    function getBalance(address token) external view returns (uint);

    function getSwapFee() external view returns (uint);

    function calcPoolOutGivenSingleIn(
        uint tokenBalanceIn,
        uint tokenWeightIn,
        uint poolSupply,
        uint totalWeight,
        uint tokenAmountIn,
        uint swapFee
    ) external pure returns (uint poolAmountOut);

}

contract Curve is ReentrancyGuard, Initializable {

    address public DAO_MULTISIG_ADDR = 0xB60eF661cEdC835836896191EDB87CC025EFd0B7;
    address public DEV_MULTISIG_ADDR = 0x3c25c256E609f524bf8b35De7a517d5e883Ff81C;
    address public VESTING_MULTISIG_ADDR = address(0);  // TODO
    address public HARVEST_MULTISIG_ADDR = address(0); // TODO

    //
    uint256 private DEV_PCT_TOKEN = 5 * 10 ** 16; // 5% to Dev Multisig as base asset  4/4/21
    uint256 private DAO_PCT_ARRAY = 5 * 10 ** 16; // 5% to DAO multisig as array 4/4/21
    uint256 private DAO_PCT_TOKEN = 20 * 10 ** 16;  //20% to DAO multisig as base entered asset 4/4/21
    uint256 private PRECISION = 10 ** 18;

    uint256 private MAX_SLIPPAGE = 2 * 10 ** 16;

    uint256 public MAX_ARRAY_SUPPLY = 100000 * PRECISION;

    // Represents the 700k DAI spent for initial 10k tokens
    uint256 private STARTING_DAI_BALANCE = 700000 * PRECISION;

    // Starting supply of 10k ARRAY
    uint256 private STARTING_ARRAY_MINTED = 10000 * PRECISION;

    // Keeps track of LP tokens
    uint256 public virtualBalance;

    // Keeps track of ARRAY minted for bonding bancor
    uint256 public virtualSupply;

    // Keeps track of the max amount of ARRAY supply
    uint256 public maxSupply = 100000 * PRECISION;

    // Keeps track of DAI for team multisig
    uint256 public devFundLPBalance;

    // Keeps track of ARRAY for team multisig
    uint256 public devFundArrayBalance;

    // Keeps track of ARRAY for DAO multisig
    uint256 public daoArrayBalance;

    // Used to calculate bonding bancor slope
    // Returns same result as x^2
    //    uint32 public reserveRatio = 333333; // symbolizes 1/3, based on bancor's max of 1/1,000,000
//    uint32 public reserveRatio = 580562; // symbolizes 1/3, based on bancor's max of 1/1,000,000
    uint32 public reserveRatio = 333333; // symbolizes 1/3, based on bancor's max of 1/1,000,000

    address public owner;
    address public devFund;
    address public gov;
    using EnumerableSet for EnumerableSet.AddressSet;
    EnumerableSet.AddressSet private virtualLpTokens;

    IChainLinkFeed public constant FASTGAS = IChainLinkFeed(0x169E633A2D1E6c10dD91238Ba11c4A708dfEF37C);

    I_ARRAY public ARRAY;
    I_BancorFormula public CURVE;
    I_CRP public CRP;
    I_BPool public BP;

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
        address _gov,
        address _arrayToken,
        address _curve,
        address _smartPool,
        address _bpool
    ) {
        owner = _owner;
        gov = _gov;
        ARRAY = I_ARRAY(_arrayToken);
        CURVE = I_BancorFormula(_curve);
        CRP = I_CRP(_smartPool);
        BP = I_BPool(_bpool);
    }

    modifier validGasPrice() {
        require(
            tx.gasprice <= uint(FASTGAS.latestAnswer()),
            "Must send equal to or lower than fast gas price to mitigate front running attacks."
        );
        _;
    }

    function initialize(uint256 initialAmountLPToken) public initializer {
        require(msg.sender == owner, "!owner");

        // Send LP tokens from owner to balancer
        require(CRP.transferFrom(owner, address(this), initialAmountLPToken), "Transfer failed");

        // Mint ARRAY to CCO
        ARRAY.mint(DAO_MULTISIG_ADDR, STARTING_ARRAY_MINTED);

        virtualBalance = initialAmountLPToken;
        virtualSupply = STARTING_ARRAY_MINTED;
    }


    function buy(address token, uint256 amount) public nonReentrant validGasPrice returns (uint256 returnAmount) {
        IERC20 _token = IERC20(token);

        require(this.isTokenInLP(token)); // dev: token not in part of collateral
        require(this.isTokenInVirtualLP(token)); // dev: token not greenlisted
        require(amount > 0); // dev: amount is 0
        require(_token.allowance(msg.sender, address(this)) >= amount); // dev: user allowance < amount
        require(_token.balanceOf(msg.sender) >= amount); // dev: user balance < amount

        uint256 max_in_balance = BP.getBalance(token) / 2;
        require(amount <= max_in_balance); // dev: ratio in to high

        require(_token.transferFrom(msg.sender, address(this), amount)); // dev: transfer to contract failed"
        require(_token.balanceOf(address(this)) >= amount); // dev: contract did not receive enough token

        // 20% goes to DAO MultiSig in original token
        uint256 amountTokensForDAOMultiSig = amount * DAO_PCT_TOKEN / PRECISION;
        require(_token.transfer(DAO_MULTISIG_ADDR, amountTokensForDAOMultiSig), "transfer to DAO Multisig failed");

        // 5% goes to Dev MultiSig in original token
        uint256 amountTokensForDEVMultiSig = amount * DEV_PCT_TOKEN / PRECISION;
        require(_token.transfer(DEV_MULTISIG_ADDR, amountTokensForDEVMultiSig), "transfer to DEV Multisig failed");

        // what's left will be used to get LP tokens
        uint256 amountTokensForLP = amount - amountTokensForDAOMultiSig - amountTokensForDEVMultiSig;

        require(_token.approve(address(CRP), amountTokensForLP), "token approve for contract to balancer pool failed");

        // calculate the estimated LP tokens that we'd get and then adjust for slippage to have minimum
        uint256 maxLpTokenAmount = _calculateLPTokensGivenERC20Tokens(token, amountTokensForLP);
        uint256 minLpTokenAmount = maxLpTokenAmount * MAX_SLIPPAGE / PRECISION;


        // send the pool the left over tokens for LP, expecting minimum return
        uint256 lpTokenAmount = CRP.joinswapExternAmountIn(address(_token), amountTokensForLP, 0);

        // calculate how many array tokens correspond to the LP tokens that we got
        uint256 amountArrayToMint = _calculateArrayGivenLPTokenAMount(lpTokenAmount);
        require(amountArrayToMint + virtualSupply <= maxSupply); // dev: minted array > total supply

        // take off the cut for the multisig
        uint256 amountArrayForDAOMultisig = amountArrayToMint * DAO_PCT_ARRAY / PRECISION;
        ARRAY.mint(DAO_MULTISIG_ADDR, amountArrayForDAOMultisig);

        // rest goes to user
        uint256 amountArrayForUser = amountArrayToMint - amountArrayForDAOMultisig;
        ARRAY.mint(msg.sender, amountArrayForUser);

        // update virtual balance and supply
        virtualBalance = virtualBalance + lpTokenAmount;
        virtualSupply = virtualSupply + amountArrayToMint;

        emit Buy(msg.sender, token, amount, lpTokenAmount, amountArrayForUser);
        return returnAmount = amountArrayForUser;
    }


    function sell(uint256 amountArray) public nonReentrant validGasPrice returns (uint256 returnAmount) {
        returnAmount = _sell(amountArray);
    }

    function sell(bool max) public nonReentrant returns (uint256 returnAmount) {
        uint256 amountArray = ARRAY.balanceOf(msg.sender);
        returnAmount = _sell(amountArray);
    }

    function _sell(uint256 amountArray) internal returns (uint256 returnAmount) {

        require(amountArray <= ARRAY.balanceOf(msg.sender)); // dev: user balance < amount

        // get total supply of array token, subtract amount burned
        uint256 amountArrayAfterBurn = virtualSupply - amountArray;

        // calculate how much of the LP token the burner gets
        uint256 amountLPTokenReturned = calculateLPtokensGivenArrayTokens(amountArray);

        // burn token
        ARRAY.burn(msg.sender, amountArray);

        // send to user
        require(CRP.transfer(msg.sender, amountLPTokenReturned)); // dev: transfer of lp token to user failed

        // update virtual balance and supply
        virtualBalance = virtualBalance - amountLPTokenReturned;
        virtualSupply = virtualSupply - amountArray;

        emit Sell(msg.sender, amountArray, amountLPTokenReturned);
        return returnAmount = amountLPTokenReturned;
    }


    function calculateArrayTokensGivenERC20Tokens(address token, uint256 amount) public view returns
    (uint256 amountArrayForUser)
    {
        require(this.isTokenInVirtualLP(token)); // dev: token not in virtual LP
        require(this.isTokenInLP(token)); // dev: token not in balancer LP

        uint256 amountTokensForDAOMultiSig = amount * DAO_PCT_TOKEN / PRECISION;
        uint256 amountTokensForDEVMultiSig = amount * DEV_PCT_TOKEN / PRECISION;
        uint256 amountTokensForLP = amount - amountTokensForDAOMultiSig - amountTokensForDEVMultiSig;

        uint256 maxLpTokenAmount = _calculateLPTokensGivenERC20Tokens(token, amountTokensForLP);
        uint256 amountArrayToMint = _calculateArrayGivenLPTokenAMount(maxLpTokenAmount);

        uint256 amountArrayForDAOMultisig = amountArrayToMint * DAO_PCT_ARRAY / PRECISION;

        return amountArrayForUser = amountArrayToMint - amountArrayForDAOMultisig;
    }

    function calculateLPtokensGivenArrayTokens(uint256 amount) public returns (uint256 amountLPToken)
    {

        // Calculate quantity of ARRAY minted based on total LP tokens
        return amountLPToken = CURVE.calculateSaleReturn(
            virtualSupply,
            virtualBalance,
            reserveRatio,
            amount
        );

    }

    function _calculateLPTokensGivenERC20Tokens(address token, uint256 amount) private view returns (uint256 amountLPToken)
    {

        uint256 weight = BP.getDenormalizedWeight(token);
        uint256 totalWeight = BP.getTotalDenormalizedWeight();
        uint256 balance = BP.getBalance(token);
        uint256 fee = BP.getSwapFee();
        uint256 supply = CRP.totalSupply();

        return BP.calcPoolOutGivenSingleIn(balance, weight, supply, totalWeight, amount, fee);
    }

    function _calculateArrayGivenLPTokenAMount(uint256 amount) private view returns (uint256 amountArrayToken)
    {
        // Calculate quantity of ARRAY minted based on total LP tokens
        return amountArrayToken = CURVE.calculatePurchaseReturn(
            virtualSupply,
            virtualBalance,
            reserveRatio,
            amount
        );
    }

    /**
    @dev Checks if given token is part of the balancer pool
    @param token Token to be checked.
    @return bool Whether or not it's part
*/

    function isTokenInLP(address token) external view returns (bool) {
        address[] memory lpTokens = BP.getCurrentTokens();
        for (uint256 i = 0; i < lpTokens.length; i++) {
            if (token == lpTokens[i]) {
                return true;
            }
        }
        return false;
    }

    /**
    @dev Checks if given token is part of the tokens that are allowed to add to the balancer pool
    @param token Token to be checked.
    @return contains Whether or not it's part
*/

    function isTokenInVirtualLP(address token) external view returns (bool contains) {
        return contains = virtualLpTokens.contains(token);
    }

    function addTokenToVirtualLP(address token) public returns (bool success){
        require(msg.sender == gov, "msg.sender != gov");
        require(this.isTokenInLP(token), "Token not in Balancer LP");

        return success = virtualLpTokens.add(token);
    }

    function removeTokenFromVirtualLP(address token) public returns (bool success) {
        require(msg.sender == gov, "msg.sender != gov");
        require(this.isTokenInVirtualLP(token), "Token not in Virtual LP");

        return success = virtualLpTokens.remove(token);
    }

}
