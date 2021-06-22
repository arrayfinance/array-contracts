//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.2;

import "../../node_modules/@openzeppelin/contracts/utils/Address.sol";
import "../../node_modules/@openzeppelin/contracts/access/AccessControl.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract NoopStrategy {
  using SafeERC20 for IERC20;
  using Address for address;

  address public underlying;
  address public vault;
  IAccessControl public roles;

  bool public withdrawAllCalled = false;

  constructor(address _underlying, address _vault, address _roles)
  {
    require(_underlying != address(0), "_underlying cannot be empty");
    require(_vault != address(0), "_vault cannot be empty");
    require(_roles != address(0), "_roles cannot be empty");

    underlying = _underlying;
    vault = _vault;
    roles = IAccessControl(_roles);
  }

  modifier restricted() {
    require(msg.sender == vault || roles.hasRole(keccak256('DEVELOPER'), msg.sender));
    _;
  }

  /*
  * Returns the total invested amount.
  */
  function investedUnderlyingBalance()
  public
  view
  returns (uint256)
  {
    return IERC20(underlying).balanceOf(address(this));
  }

  // Invests all tokens that were accumulated so far
  function investAllUnderlying() public {
  }

  function withdrawAllToVault()
  external
  restricted
  {
    withdrawAllCalled = true;
    if (IERC20(underlying).balanceOf(address(this)) > 0) {
      IERC20(underlying).safeTransfer(vault, IERC20(underlying).balanceOf(address(this)));
    }
  }

  function withdrawToVault(uint256 amount)
  external
  restricted
  {
    if (amount > 0) {
      IERC20(underlying).safeTransfer(vault, amount);
    }
  }

  function doStuff() external restricted {
    // a no-op
  }
}
