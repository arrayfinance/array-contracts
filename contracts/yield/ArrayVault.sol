//SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/IERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/AddressUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ContextUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/math/MathUpgradeable.sol";

import "../interfaces/IArrayStrategy.sol";
import "../access/ArrayRolesStorage.sol";


/**
 * @notice PROXIED, CHANGING ORDER/TYPE OF STORAGE VARIABLES WILL BREAK THINGS IF IMPLEMENTING IN SAME PROXY
 * @dev Basic vault contract, stripped down version of harvest's implementation.
 *
 * 'Any intelligent fool can make things bigger and more complex... It takes a touch of genius - and lot of courage
 * to move in the opposite direction' - Albert Einstein.
 **/

contract ArrayVault is ERC20Upgradeable, ArrayRolesStorage, OwnableUpgradeable {
    using SafeERC20Upgradeable for IERC20Upgradeable;
    using AddressUpgradeable for address;
    //    IAccessControlUpgradeable public roles;

    event Withdraw(address indexed beneficiary, uint256 amount);
    event Deposit(address indexed beneficiary, uint256 amount);
    event Invest(uint256 amount);
    event StrategyChanged(address newStrategy, address oldStrategy);

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /*********************/
    /*    STATE (PROXY)  */
    /*********************/
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    address public underlying; // don't change me
    address public strategy; // don't change me please
    uint256 public toinvestNumerator; // don't change me it hurts
    uint256 public toInvestDenominator; // leave me be
    uint256 public precision = 10 ** 18;



    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /*********************/
    /*    SETUP        */
    /*********************/
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function initialize
    (
        address _roles,
        address _underlying,
        address _strategy,
        uint256 _toInvestNumerator,
        uint256 _toInvestDenominator
    )
    public
    initializer

    {
        // check input
        require(_toInvestNumerator <= _toInvestDenominator);
        // dev: can't invest more than 100%
        require(_toInvestDenominator != 0, "cannot divide by 0");
        // dev: denominator can't be 0
        require(AddressUpgradeable.isContract(_underlying));
        // dev: underlying must be contract
        require(AddressUpgradeable.isContract(_roles));
        // dev: roles must be contract
        require(AddressUpgradeable.isContract(_strategy));
        // dev: strategy must be contract

        ArrayRolesStorage.initialize(_roles);

        __Context_init_unchained();
        __Ownable_init_unchained();

        // set storage
        underlying = _underlying;
        strategy = _strategy;
        toinvestNumerator = _toInvestNumerator;
        toInvestDenominator = _toInvestDenominator;


        // set up erc20 contract of vault
        __ERC20_init
        (
            string(abi.encodePacked("array_", ERC20Upgradeable(_underlying).symbol())),
            string(abi.encodePacked("a_", ERC20Upgradeable(_underlying).symbol()))
        );
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /*********************/
    /*    VAULT           */
    /*********************/
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function underlyingBalanceInVault()
    view
    public
    returns (uint256)
    {
        return IERC20Upgradeable(underlying).balanceOf(address(this));
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function underlyingBalanceWithInvestment()
    view
    public
    returns (uint256)
    {
        if (address(strategy) == address(0))
        {
            return underlyingBalanceInVault();
        }
        return underlyingBalanceInVault() + IArrayStrategy(strategy).investedUnderlyingBalance();
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function getPricePerFullShare()
    public
    view
    returns (uint256)
    {
        if (totalSupply() == 0) {
            return precision;
        } else {
            return precision * underlyingBalanceWithInvestment() / totalSupply();
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function underlyingBalanceWithInvestmentForHolder(address holder)
    view
    external
    returns (uint256)
    {
        if (totalSupply() == 0)
        {
            return 0;
        }
        return underlyingBalanceWithInvestment() * balanceOf(holder) / totalSupply();
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function rebalance()
    external
    onlyDev
    {
        withdrawAll();
        invest();
    }

    /*********************/
    /*    STRATEGY       */
    /*********************/

    function availableToInvestOut()
    public
    view
    returns (uint256) {

        uint256 wantInvestInTotal = underlyingBalanceWithInvestment() * toinvestNumerator / toInvestDenominator;
        uint256 alreadyInvested = IArrayStrategy(strategy).investedUnderlyingBalance();

        if (alreadyInvested >= wantInvestInTotal)
        {
            return 0;

        } else {

            uint256 remainingToInvest = wantInvestInTotal - alreadyInvested;
            return remainingToInvest <= underlyingBalanceInVault()
            ? remainingToInvest : underlyingBalanceInVault();
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function doStuff()
    onlyDev
    external
    {
        invest();
        IArrayStrategy(strategy).doStuff();
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function invest()
    internal
    {
        uint256 availableAmount = availableToInvestOut();
        if (availableAmount > 0)
        {
            IERC20Upgradeable(underlying).safeTransfer(address(strategy), availableAmount);
            emit Invest(availableAmount);
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // come home boys
    function withdrawAll()
    public
    onlyDev
    {
        IArrayStrategy(strategy).withdrawAllToVault();
    }

    function setStrategy(address _strategy)
    public
    onlyTimelock
    {
        require(_strategy != address(0), "new _strategy cannot be empty");
        require(IArrayStrategy(_strategy).underlying() == address(underlying), "Vault underlying must match Strategy underlying");
        require(IArrayStrategy(_strategy).vault() == address(this), "the strategy does not belong to this vault");

        emit StrategyChanged(_strategy, strategy);

        if (address(_strategy) != address(strategy)) {
            if (address(strategy) != address(0)) {
                IERC20Upgradeable(underlying).safeApprove(address(strategy), 0);
                IArrayStrategy(strategy).withdrawAllToVault();
            }

            strategy = _strategy;
            IERC20Upgradeable(underlying).safeApprove(address(strategy), 0);
            IERC20Upgradeable(underlying).safeApprove(address(strategy), type(uint256).max);
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /*********************/
    /*      USER         */
    /*********************/
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function deposit(uint256 amount) external {
        _deposit(amount, msg.sender, msg.sender);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function depositFor(uint256 amount, address holder) public {
        _deposit(amount, msg.sender, holder);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function _deposit(uint256 amount, address sender, address beneficiary) internal {

        require(amount > 0);
        // dev: Cannot deposit 0
        require(beneficiary != address(0));
        // dev: holder must be defined
        require(IERC20Upgradeable(underlying).allowance(sender, address(this)) >= amount);
        // dev: need approval

        // totalSupply * getPricePerFullShare = underlyingBalanceWithInvestment
        uint256 toMint = totalSupply() == 0
        ? amount
        : (amount * totalSupply()) / underlyingBalanceWithInvestment();

        _mint(beneficiary, toMint);
        IERC20Upgradeable(underlying).safeTransferFrom(sender, address(this), amount);

        // update the contribution amount for the beneficiary
        emit Deposit(beneficiary, amount);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    function withdraw(uint256 numberOfShares)
    external
    {

        require(totalSupply() > 0, "Vault has no shares");
        require(numberOfShares > 0, "numberOfShares must be greater than 0");

        uint256 totalSupply = totalSupply();

        _burn(msg.sender, numberOfShares);

        uint256 underlyingAmountToWithdraw = underlyingBalanceWithInvestment() * numberOfShares / totalSupply;

        if (underlyingAmountToWithdraw > underlyingBalanceInVault())

        {
            // withdraw everything from the strategy to accurately check the share value
            if (numberOfShares == totalSupply) {
                IArrayStrategy(strategy).withdrawAllToVault();
            } else {
                uint256 missing = underlyingAmountToWithdraw - underlyingBalanceInVault();
                IArrayStrategy(strategy).withdrawToVault(missing);
            }
            // recalculate to improve accuracy
            underlyingAmountToWithdraw = MathUpgradeable.min(underlyingBalanceWithInvestment()
            * numberOfShares / totalSupply,
                underlyingBalanceInVault());
        }

        IERC20Upgradeable(underlying).safeTransfer(msg.sender, underlyingAmountToWithdraw);
        // dev: can't withdraw

        // update the withdrawal amount for the holder
        emit Withdraw(msg.sender, underlyingAmountToWithdraw);
    }

}
