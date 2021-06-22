// SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.2;
import "../../node_modules/@openzeppelin/contracts/token/ERC20/IERC20.sol";


interface IArray is IERC20 {
    function mint(address to, uint256 amount) external;
    function burn(address from, uint256 amount) external;
}
