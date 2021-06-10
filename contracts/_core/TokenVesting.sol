// SPDX-License-Identifier: Unlicense

pragma solidity 0.8.4;
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


contract TokenVesting is Ownable {
    event TokensReleased(address token, uint256 amount);

    // beneficiary of tokens after they are released
    address public immutable beneficiary = 0x3c25c256E609f524bf8b35De7a517d5e883Ff81C; //dev multisig addr
    IERC20 public immutable token = IERC20(address(0)); //todo: add array token address

    // Durations and timestamps are expressed in UNIX time, the same units as block.timestamp.
    uint256 public cliff;
    uint256 public start;
    uint256 public duration;
    uint256 public released;

    constructor (uint256 _start, uint256 _duration, uint256 _cliffDuration) {
        require(_cliffDuration <= _duration, "TokenVesting: cliff is longer than duration");
        require(_duration > 0, "TokenVesting: duration is 0");
        require(_start + _duration > block.timestamp, "TokenVesting: final time is before current time");

        start = _start;
        duration = _duration;
        cliff = _start + _cliffDuration;
        
    }


    function release() external {
        uint256 unreleased = _releasableAmount();

        require(unreleased > 0, "TokenVesting: no tokens are due");

        require(token.transfer(beneficiary, unreleased), "Transfer failed"); 

        released = released + unreleased;
        emit TokensReleased(address(token), unreleased);
    }
    

    function _releasableAmount() private view returns (uint256) {
        return _vestedAmount() - released;
    }

    function vested() external view returns (uint256) {
        return _vestedAmount();
    }

    function _vestedAmount() private view returns (uint256) {
        uint256 currentBalance = token.balanceOf(address(this));
        uint256 totalBalance = currentBalance + released;

        if (block.timestamp < cliff) {
            return 0;
        } else if (block.timestamp >= start + duration) {
            return totalBalance;
        } else {
            return totalBalance * (block.timestamp - start) / duration;
        }
    }

}
