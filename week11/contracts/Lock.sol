// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Lock
 * @notice 11주차 실습 — Hardhat 로컬 개발 기본 컨트랙트
 *
 * 기능: 특정 시간까지 ETH를 잠금, 이후 소유자가 인출 가능
 * 교육 목적: Hardhat 테스트, 배포 스크립트, 이벤트 활용 방법 학습
 */
contract Lock {
    uint256 public unlockTime;
    address payable public owner;

    event Withdrawal(uint256 amount, uint256 when);

    constructor(uint256 _unlockTime) payable {
        require(
            block.timestamp < _unlockTime,
            "Unlock time should be in the future"
        );
        unlockTime = _unlockTime;
        owner = payable(msg.sender);
    }

    function withdraw() public {
        require(block.timestamp >= unlockTime, "You can't withdraw yet");
        require(msg.sender == owner, "You aren't the owner");

        uint256 amount = address(this).balance;
        emit Withdrawal(amount, block.timestamp);
        owner.transfer(amount);
    }
}
