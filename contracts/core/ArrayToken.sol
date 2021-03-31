// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/Context.sol";
import "@openzeppelin/contracts/access/AccessControlEnumerable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract ArrayToken is Context, AccessControlEnumerable, ERC20 {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("PAUSER_ROLE");

    constructor(string memory name, string memory symbol, address curveController)
    ERC20(name, symbol)

    {
        _setupRole(DEFAULT_ADMIN_ROLE, _msgSender());
        _setupRole(MINTER_ROLE, curveController);
        _setupRole(BURNER_ROLE, curveController);
    }

    function mint(address to, uint256 amount) external virtual {
        require(hasRole(MINTER_ROLE, _msgSender()), "ArrayToken: must have minter role to mint");
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external virtual {
        require(hasRole(BURNER_ROLE, _msgSender()), "ArrayToken: must have burner role to burn");
        _burn(from, amount);
    }

}
