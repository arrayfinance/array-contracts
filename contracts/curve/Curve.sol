// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

interface I_ERC20 {

    function mint(address _to, uint256 amount) external;

    function burn(address _from, uint256 amount) external;

    function transferFrom(address _from, address _to, uint256 _value) external returns (bool success);

    function transfer(address _to, uint256 _value) external returns (bool success);

    function balanceOf(address _owner) external view returns (uint256 balance);

    function allowance(address _owner, address _spender) external view returns (uint256 amount);

    function approve(address _spender, uint256 _value) external returns (bool success);
}

interface I_BancorFormula {
    function calculatePurchaseReturn(uint256 _supply, uint256 _reserveBalance, uint32 _reserveWeight, uint256 _amount)
    external view returns (uint256);
}

interface I_CRP {
    function mintPoolShareFromLib(uint amount) external;

    function pushPoolShareFromLib(address to, uint amount) external;

    function pullPoolShareFromLib(address from, uint amount) external;

    function burnPoolShareFromLib(uint amount) external;

    function totalSupply() external view returns (uint);

    function getController() external view returns (address);

    function transfer(address dst, uint amt) external returns (bool);

    function transferFrom(
        address src, address dst, uint amt
    ) external returns (bool);

    function balanceOf(address whom) external view returns (uint);

    function allowance(address src, address dst) external view returns (uint);

    function approve(address dst, uint amt) external returns (bool);

    function joinPool(uint poolAmountOut, uint[] calldata maxAmountsIn) external;

    function exitPool(uint poolAmountIn, uint[] calldata minAmountsOut) external;

    function bPool() external view returns (address);

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
}

interface I_BPool {

    function MAX_IN_RATIO() external view returns (uint);

    function MAX_OUT_RATIO() external view returns (uint);


    function getNumTokens() external view returns (uint);

    function getCurrentTokens() external view returns (address[] memory tokens);

    function getDenormalizedWeight(address token) external view returns (uint);

    function getTotalDenormalizedWeight() external view returns (uint);

    function getNormalizedWeight(address token) external view returns (uint);

    function getBalance(address token) external view returns (uint);

    function getSwapFee() external view returns (uint);

    function getController() external view returns (address);

    // @dev calculates how much pool token you'd get putting in a certain token, this token is defined by balance,
    //      weight
    //      tokenBalanceIn, tokenWeightIn, totalWeight, swapFee are from the bpool
    //      poolSupply is from the spool
    function calcPoolOutGivenSingleIn(
        uint tokenBalanceIn,
        uint tokenWeightIn,
        uint poolSupply,
        uint totalWeight,
        uint tokenAmountIn,
        uint swapFee
    ) external pure returns (uint poolAmountOut);

    // @dev calculates how much pool token you'd get putting in a certain token, this token is defined by balance,
    //      weight
    //      tokenBalanceIn, tokenWeightIn, totalWeight, swapFee are from the bpool
    //      poolSupply is from the spool
    function calcSingleInGivenPoolOut(
        uint tokenBalanceIn,
        uint tokenWeightIn,
        uint poolSupply,
        uint totalWeight,
        uint poolAmountOut,
        uint swapFee
    ) external pure returns (uint tokenAmountIn);

}

contract Curve is ReentrancyGuard, Initializable {

    address public DAO_MULTISIG_ADDR = 0xB60eF661cEdC835836896191EDB87CC025EFd0B7;
    address public DEV_MULTISIG_ADDR = 0x3c25c256E609f524bf8b35De7a517d5e883Ff81C;
    address public VESTING_MULTISIG_ADDR = address(0);  // TODO
    address public HARVEST_MULTISIG_ADDR = address(0); // TODO

    //
    uint256 private DEV_PCT_TOKEN = 5 * 10 ** 16; // 5% to Dev Multisig as base asset  4/4/21
    uint256 private DAO_PCT_ARRAY = 5 * 10 ** 16; // 5% to DAO multisig as base entered asset 4/4/21
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
    uint32 public reserveRatio = 333333; // symbolizes 1/3, based on bancor's max of 1/1,000,000

    address public owner;
    address public devFund;
    address public gov;
    using EnumerableSet for EnumerableSet.AddressSet;
    EnumerableSet.AddressSet private virtualLpTokens;

    I_ERC20 public ARRAY;
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
        address _smartPool
    ) {
        owner = _owner;
        gov = _gov;
        ARRAY = I_ERC20(_arrayToken);
        CURVE = I_BancorFormula(_curve);
        CRP = I_CRP(_smartPool);
    }

    function initialize(uint256 initialAmountLPToken) public initializer {
        require(msg.sender == owner, "!owner");

        // @dev sets the balancer pool that's needed to get balances of individual tokens, etc..
        BP = I_BPool(CRP.bPool());

        // Send LP tokens from owner to balancer
        require(CRP.transferFrom(owner, address(this), initialAmountLPToken), "Transfer failed");

        // Mint ARRAY to CCO
        ARRAY.mint(DAO_MULTISIG_ADDR, STARTING_ARRAY_MINTED);

        virtualBalance = initialAmountLPToken;
        virtualSupply = STARTING_ARRAY_MINTED;
    }


    function buy(address token, uint256 amount) public nonReentrant {
        I_ERC20 _token = I_ERC20(token);

        require(this.isTokenInLP(token), "Token not in LP");
        require(this.isTokenInVirtualLP(token), "Token not greenlisted");
        require(_token.allowance(msg.sender, address(this)) >= amount, "Not enough allowance");
        require(amount > 0, "buy: cannot deposit 0 tokens");

        require(_token.transferFrom(msg.sender, address(this), amount), 'transferFrom failed.');
        require(_token.balanceOf(address(this)) >= amount, "Contract does not have enough token");

        // 20% goes to DAO MultiSig in original token
        uint256 amountTokensForDAOMultiSig = amount * DAO_PCT_TOKEN / PRECISION;
        require(_token.transfer(DAO_MULTISIG_ADDR, amountTokensForDAOMultiSig), "Transfer to DAO Multisig failed");

        // 5% goes to Dev MultiSig in original token
        uint256 amountTokensForDEVMultiSig = amount * DAO_PCT_TOKEN / PRECISION;
        require(_token.transfer(DEV_MULTISIG_ADDR, amountTokensForDEVMultiSig), "Transfer to DEV Multisig failed");

        // what's left will be used to get LP tokens
        uint256 amountTokensForLP = amount - amountTokensForDAOMultiSig - amountTokensForDEVMultiSig;

        require(_token.balanceOf(address(this)) >= amountTokensForLP, "Not enough tokens in Contract");
        require(_token.approve(address(CRP), amountTokensForLP), 'approve failed');

        // calculate the estimated LP tokens that we'd get and then adjust for slippage to have minimum
        uint256 maxLpTokenAmount = _calculateLPTokensGivenERC20Tokens(token, amountTokensForLP);
        uint256 minLpTokenAmount = maxLpTokenAmount * MAX_SLIPPAGE / PRECISION;

        // send the pool the left over tokens for LP, expecting minimum return
        uint256 lpTokenAmount = CRP.joinswapExternAmountIn(address(_token), amountTokensForLP, minLpTokenAmount);

        // calculate how many array tokens correspond to the LP tokens that we got
        uint256 amountArrayToMint = _calculateArrayGivenLPTokenAMount(lpTokenAmount);
        require(amountArrayToMint <= maxSupply, "buy: amountArrayMinted > max supply");

        // take off the cut for the multisig
        uint256 amountArrayForDAOMultisig = amountArrayToMint * DAO_PCT_ARRAY / PRECISION;
        ARRAY.mint(DAO_MULTISIG_ADDR, amountArrayForDAOMultisig);

        // rest goes to user
        uint256 amountArrayForUser = amountArrayToMint - amountArrayForDAOMultisig;
        ARRAY.mint(msg.sender, amountArrayForUser);

        //        devFundLPBalance = devFundLPBalance + amountLPTokenDevFund;
        //        devFundArrayBalance = devFundArrayBalance + amountArrayDevFund;
        //        daoArrayBalance = daoArrayBalance + amountArrayDao;

        // update virtual balance and supply
        virtualBalance = virtualBalance + lpTokenAmount;
        virtualSupply = virtualSupply + amountArrayToMint;

        emit Buy(msg.sender, token, amount, lpTokenAmount, amountArrayForUser);
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

    // @TODO why does user have to speciy amount when swapping MAX?
    function sell(uint256 amountArray) public nonReentrant returns (bool success) {
        success = _sell(amountArray);
    }

    function sell(bool max) public nonReentrant returns (bool success) {
        uint256 amountArray = ARRAY.balanceOf(msg.sender);
        success = _sell(amountArray);
    }

    function _sell(uint256 amountArray) internal returns (bool success) {

        require(ARRAY.balanceOf(msg.sender) <= amountArray, "Cannot burn more than amount");

        // get total supply of array token, subtract amount burned
        uint256 amountArrayAfterBurn = virtualSupply - amountArray;

        // get % of burned supply
        uint256 pctArrayBurned = amountArrayAfterBurn * PRECISION / virtualSupply;

        // calculate how much of the LP token the burner gets
        uint256 amountLPTokenReturned = pctArrayBurned * virtualBalance / PRECISION;

        // burn token
        ARRAY.burn(msg.sender, amountArray);

        // send to burner
        require(CRP.transfer(msg.sender, amountLPTokenReturned), "Transfer failed");

        // update virtual balance and supply
        virtualBalance = virtualBalance - amountLPTokenReturned;
        virtualSupply = virtualSupply - amountArray;

        emit Sell(msg.sender, amountArray, amountLPTokenReturned);
        return success = true;
    }


    //    function withdrawDevFunds(address token, uint256 amount, bool max) external returns (bool) {
    //        bool success = false;
    //
    //        require(msg.sender == DEV_MULTISIG_ADDR, "withdrawDevFunds: msg.sender != DEV_MULTISIG_ADDR");
    //
    //
    //        if (token == address(ARRAY)) {
    //            require(amount <= devFundArrayBalance);
    //            if (max) {amount = devFundArrayBalance;}
    ////            require(ARRAY.mint(VESTING_MULTISIG_ADDR, amount)); // @TODO this doesn't return a bool.
    //            devFundArrayBalance = devFundArrayBalance - amount;
    //            success = true;
    //
    //        } else {
    //
    //            require(amount <= devFundLPBalance);
    //            if (max) {amount = devFundLPBalance;}
    //            require(DAI.transfer(DEV_MULTISIG_ADDR, amount));
    //            devFundLPBalance = devFundLPBalance - amount;
    //            success = true;
    //        }
    //
    //        emit WithdrawDevFunds(token, amount);
    //        emit WithdrawDaoFunds(amount);
    //
    //        return success;
    //
    //    }

    // // // // // // // // // // // // // //
    // @TODO this needs extensive testing !!!
    // // // // // // // // // // // // // //

    function calculateArrayTokensGivenERC20Tokens(address token, uint256 amount) public returns (uint256
        amountArrayToken)
    {
        require(this.isTokenInVirtualLP(token), "Token not in Virtual LP");
        require(this.isTokenInLP(token), "Token not in Balancer LP");

        uint256 amountLPToken = _calculateLPTokensGivenERC20Tokens(token, amount);
        return _calculateArrayGivenLPTokenAMount(amountLPToken);
    }


    function _calculateLPTokensGivenERC20Tokens(address token, uint256 amount) private returns (uint256 amountLPToken)
    {

        uint256 weight = BP.getDenormalizedWeight(token);
        uint256 totalWeight = BP.getTotalDenormalizedWeight();
        uint256 balance = BP.getBalance(token);
        uint256 fee = BP.getSwapFee();
        uint256 supply = CRP.totalSupply();

        return BP.calcPoolOutGivenSingleIn(balance, weight, supply, totalWeight, amount, fee);
    }


    function _calculateArrayGivenLPTokenAMount(uint256 amount) private returns (uint256 amountArrayToMintNormalized)
    {
        // Calculate quantity of ARRAY minted based on total LP tokens
        uint256 amountArrayToMint = CURVE.calculatePurchaseReturn(
            virtualSupply,
            virtualBalance,
            reserveRatio,
            amount
        );

        return amountArrayToMint;
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

    function _notOverMaxInBalance(uint256 amount, address token) private view returns (bool isUnder){
        uint256 _max = BP.MAX_IN_RATIO();
        uint256 bal = BP.getBalance(token);


    }

}
