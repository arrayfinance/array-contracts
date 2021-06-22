// SPDX-License-Identifier: Unlicense

pragma solidity ^0.8.2;

import "../../node_modules/@openzeppelin/contracts/utils/Context.sol";
import "../../node_modules/@openzeppelin/contracts/access/AccessControl.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract ArrayToken is Context, AccessControl, ERC20 {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");

    constructor(string memory name, string memory symbol)
    ERC20(name, symbol)

    {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, address(0));
        _setupRole(BURNER_ROLE, address(0));
    }

    function mint(address to, uint256 amount)
    external
    virtual
    onlyRole(MINTER_ROLE)
    {
        _mint(to, amount);
    }

    function burn(address from, uint256 amount)
    external
    virtual
    onlyRole(BURNER_ROLE)
    {
        _burn(from, amount);
    }

}
