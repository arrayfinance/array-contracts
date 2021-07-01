// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

// openzeppelin stuff
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

// custom stuff
import "../utils/GasPrice.sol";
import "../access/ArrayRolesStorage.sol";

// interfaces
import "../interfaces/IArrayToken.sol";
import "../interfaces/IBancorFormula.sol";
import "../interfaces/ISmartPool.sol";
import "../interfaces/IBPool.sol";


contract Curve is ReentrancyGuard, ArrayRolesStorage, GasPrice{

    address private DAO_MULTISIG_ADDRESS = address(0xB60eF661cEdC835836896191EDB87CC025EFd0B7);
    address private DEV_MULTISIG_ADDRESS = address(0x3c25c256E609f524bf8b35De7a517d5e883Ff81C);
    uint256 private PRECISION = 10 ** 18;

    // Represents the 700k DAI spent for initial 10k tokens
    uint256 private STARTING_DAI_BALANCE = 700000 * PRECISION;

    // Starting supply of 10k ARRAY
    uint256 private STARTING_ARRAY_MINTED = 10000 * PRECISION;

    IBancorFormula private bancorFormula = IBancorFormula(0xA049894d5dcaD406b7C827D6dc6A0B58CA4AE73a);
    uint32 public reserveRatio = 33333;

    uint256 private devPctToken = 10 * 10 ** 16;
    uint256 private daoPctToken = 20 * 10 ** 16;

    // Keeps track of LP tokens
    uint256 public virtualBalance;

    uint256 public devBalanceArray;
    uint256 public devBalanceLP;
    uint256 public daoBalanceArray;

    // Keeps track of ARRAY minted for bonding bancor
    uint256 public virtualSupply;

    uint256 public maxSupply = 100000 * PRECISION;

    using EnumerableSet for EnumerableSet.AddressSet;
    EnumerableSet.AddressSet private virtualLpTokens;

    IArray public arrayToken;

    ISmartPool public arraySmartPool;

    IBPool public arrayBalancerPool = IBPool(0x02e1300a7e6c3211c65317176cf1795f9bb1daab);


    event Buy(
        address from,
        address token,
        uint256 amount,
        uint256 amountLPTokenDeposited,
        uint256 amountArrayMinted
    );

    event Sell(
        address from,
        uint256 amountArray,
        uint256 amountReturnedLP
    );

    constructor() {
        owner = msg.sender;
    }


    function initialize(
        address _roles,
        address _arrayToken,
        address _bpool,
        uint256 initialAmountLPToken
    )
    public initializer
    {
        arrayToken = IArray(_arrayToken);
        arrayBalancerPool = IBPool(_bpool);        

        // Send LP tokens from owner to balancer
        require(arraySmartPool.transferFrom(DAO_MULTISIG_ADDRESS, address(this), initialAmountLPToken), "Transfer failed");
        ArrayRolesStorage.initialize(_roles);

        // Mint ARRAY to CCO
        arrayToken.mint(DAO_MULTISIG_ADDRESS, STARTING_ARRAY_MINTED);

        virtualBalance = initialAmountLPToken;
        virtualSupply = STARTING_ARRAY_MINTED;
    }

    /*  @dev
        @param token token address
        @param amount quantity in Wei
        @param slippage in percent, ie 2 means user accepts to receive 2% less than what is calculated
        */

    function buy(IERC20 token, uint256 amount, uint256 slippage )
    public
    nonReentrant
    validGasPrice
    returns (uint256 returnAmount)
    {

        require(this.isTokenInLP(token), 'token not in lp');
        require(this.isTokenInVirtualLP(token), 'token not greenlisted');
        require(amount > 0, 'amount is 0');
        require(token.allowance(msg.sender, address(this)) >= amount, 'user allowance < amount');
       
        require(token.balanceOf(msg.sender) >= amount, 'user balance < amount');

        uint256 max_in_balance = (arrayBalancerPool.getBalance(token) / 2) + 5;
        require(amount <= max_in_balance, 'ratio in too high');

        uint256 amountArrayForDao = amount * daoPctToken / PRECISION;
        uint256 amountArrayForDev = amount * devPctToken / PRECISION;

        // require(token.transfer(DAO_MULTISIG_ADDRESS, amountArrayForDao), "transfer to DAO Multisig failed");
        // require(token.transfer(DEV_MULTISIG_ADDRESS, amountArrayForDev), "transfer to DEV Multisig failed");

        // what's left will be used to get LP tokens
        uint256 amountTokensForLP = amount - amountArrayForDao - amountArrayForDev;
        require(token.approve(address(arraySmartPool), amountTokensForLP), "token approve for contract to balancer pool failed");

        // calculate the estimated LP tokens that we'd get and then adjust for slippage to have minimum
        uint256 maxLpTokenAmount = _calculateLPTokensGivenERC20Tokens(token, amountTokensForLP);
        uint256 minLpTokenAmount = maxLpTokenAmount * slippage * 10 ** 6 / PRECISION;

        // send the pool the left over tokens for LP, expecting minimum return
        uint256 lpTokenAmount = arraySmartPool.joinswapExternAmountIn(address(token), amountTokensForLP, minLpTokenAmount);

        require(token.transferFrom(msg.sender, address(this), amount), 'transfer from user to contract failed');
        require(token.balanceOf(address(this)) >= amount, 'contract did not receive the right amount of tokens');


        // calculate how many array tokens correspond to the LP tokens that we got
        uint256 amountArrayToMint = _calculateArrayGivenLPTokenAMount(lpTokenAmount);
        require(amountArrayToMint + virtualSupply <= maxSupply, 'minted array > total supply');

        arrayToken.mint(msg.sender, amountArrayToMint);

        // update virtual balance and supply
        virtualBalance = virtualBalance + lpTokenAmount;
        virtualSupply = virtualSupply + amountArrayToMint;

        emit Buy(msg.sender, token, amount, lpTokenAmount, amountArrayToMint);
        return returnAmount = amountArrayToMint;
    }

    // @dev user has either checked that he want's to sell all his tokens, in which the field to specify how much he
    //      wants to sell should be greyed out and empty and this function will be called with the signature
    //      of a single boolean set to true or it will revert. If they only sell a partial amount the function
    //      will be called with the signature uin256.

    function sell(uint256 amountArray)
    public
    nonReentrant
    validGasPrice
    returns (uint256 amountReturnedLP)
    {
        amountReturnedLP = _sell(amountArray);
    }

    function sell(bool max)
    public
    nonReentrant
    returns (uint256 amountReturnedLP)
    {
        require(max, 'sell function not called correctly');

        uint256 amountArray = arrayToken.balanceOf(msg.sender);
        amountReturnedLP = _sell(amountArray);
    }

    function _sell(uint256 amountArray)
    internal
    returns (uint256 amountReturnedLP)
    {

        require(amountArray <= arrayToken.balanceOf(msg.sender), 'user balance < amount');

        // calculate how much of the LP token the burner gets
        amountReturnedLP = calculateLPtokensGivenArrayTokens(amountArray);

        // burn token
        arrayToken.burn(msg.sender, amountArray);

        // send to user
        require(arraySmartPool.transfer(msg.sender, amountReturnedLP), 'transfer of lp token to user failed');

        // update virtual balance and supply
        virtualBalance -= amountReturnedLP;
        virtualSupply -= amountArray;

        emit Sell(msg.sender, amountArray, amountReturnedLP);
    }



    function withdrawVirtualBalance(address token, uint256 amount, bool max) external returns (bool) {

        bool success = false;
        require(
            msg.sender == DEV_MULTISIG_ADDRESS || msg.sender == DAO_MULTISIG_ADDRESS,
            "!authorized"
        );

        if (msg.sender == DEV_MULTISIG_ADDRESS && token == address(arrayToken)) {
            // withdraw from devBalanceArray
            require(
                amount > 0 && amount < devBalanceArray,
                "Amount exceeds balance"
            );
            arrayToken.mint()
        } else if (msg.sender == DAO_MULTISIG_ADDRESS && token == address(arrayToken)) {
            // withdraw from devBalanceArray
            require(
                amount > 0 && amount < devBalanceArray,
                "Amount exceeds balance"
            );
        }

        if (token == address(arrayToken)) {
            require(amount <= devBalanceArray);
            if (max) {amount = devBalanceArray;}
            
            arrayToken.mint(DAO_MULTISIG_ADDRESS, amount);

            devBalanceArray -= amount;
            success = true;
        } else {
            require(amount <= devBalancerLP);
            if (max) {amount = devBalancerLP;}

            require(DAI.transfer(DEV_MULTISIG_ADDRESS, amount));

            devBalancerLP -= amount;
            success = true;
        }
    }


    function calculateArrayMintedFromToken(address token, uint256 amount)
    public
    view
    returns (uint256 amountArrayForUser)
    {
        require(this.isTokenInVirtualLP(token), 'token not in virtual LP');
        require(this.isTokenInLP(token), 'token not in balancer LP');

        uint256 amountArrayForDao = amount * daoPctToken / PRECISION;

        // Send 10% of amount to dev fund
        uint256 amountArrayForDev = amount * devPctToken / PRECISION;

        // Use remaining 70% to LP
        uint256 amountTokensForLP = amount - amountArrayForDao - amountArrayForDev;

        uint256 maxLpTokenAmount = _calculateLPTokensGivenERC20Tokens(token, amountTokensForLP);
        uint256 amountArrayToMint = _calculateArrayGivenLPTokenAMount(maxLpTokenAmount);

        return amountArrayToMint;
    }

    function calculateLPtokensGivenArrayTokens(uint256 amount)
    public
    view
    returns (uint256 amountLPToken)
    {

        // Calculate quantity of ARRAY minted based on total LP tokens
        return amountLPToken = bancorFormula.saleTargetAmount(
            virtualSupply,
            virtualBalance,
            reserveRatio,
            amount
        );

    }

    function _calculateLPTokensGivenERC20Tokens(address token, uint256 amount)
    private
    view
    returns (uint256 amountLPToken)
    {

        uint256 weight = arrayBalancerPool.getDenormalizedWeight(token);
        uint256 totalWeight = arrayBalancerPool.getTotalDenormalizedWeight();
        uint256 balance = arrayBalancerPool.getBalance(token);
        uint256 fee = arrayBalancerPool.getSwapFee();
        uint256 supply = arraySmartPool.totalSupply();

        return arrayBalancerPool.calcPoolOutGivenSingleIn(balance, weight, supply, totalWeight, amount, fee);
    }

    function _calculateArrayGivenLPTokenAMount(uint256 amount)
    private
    view
    returns (uint256 amountArrayToken)
    {
        // Calculate quantity of ARRAY minted based on total LP tokens
        return amountArrayToken = bancorFormula.purchaseTargetAmount(
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

    function isTokenInLP(address token)
    external
    view
    returns (bool)
    {
        address[] memory lpTokens = arrayBalancerPool.getCurrentTokens();
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

    function addTokenToVirtualLP(address token)
    public
    onlyDAOMSIG
    returns (bool success){
        require(this.isTokenInLP(token), "Token not in Balancer LP");
        return success = virtualLpTokens.add(token);
    }

    function removeTokenFromVirtualLP(address token)
    public
    onlyDAOMSIG
    returns (bool success) {
        require(this.isTokenInVirtualLP(token), "Token not in Virtual LP");
        return success = virtualLpTokens.remove(token);
    }

    function setDaoPct(uint256 amount)
    public
    onlyDAOMSIG
    returns (bool success) {
        devPctToken = amount;
        success = true;
    }

    function setDevPct(uint256 amount)
    public
    onlyDAOMSIG
    returns (bool success) {
        devPctToken = amount;
        success = true;
    }

    function setMaxSupply(uint256 amount)
    public
    onlyDAOMSIG
    returns (bool success)
    {
        maxSupply = amount;
        success = true;
    }
}
