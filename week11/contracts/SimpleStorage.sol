// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title SimpleStorage
 * @notice 11주차 Hardhat 실습용 컨트랙트
 * @dev week10의 SimpleStorage에 Hardhat 테스트를 위한 추가 기능 포함
 */
contract SimpleStorage {

    uint256 private storedValue;
    address public  owner;
    uint256 public  updateCount;

    event ValueChanged(
        address indexed by,
        uint256 oldValue,
        uint256 newValue
    );

    error Unauthorized(address caller, address expected);

    modifier onlyOwner() {
        if (msg.sender != owner) {
            revert Unauthorized(msg.sender, owner);
        }
        _;
    }

    constructor(uint256 initialValue) {
        owner       = msg.sender;
        storedValue = initialValue;
        updateCount = 0;
    }

    function set(uint256 value) public {
        uint256 old = storedValue;
        storedValue  = value;
        updateCount += 1;
        emit ValueChanged(msg.sender, old, value);
    }

    function reset() public onlyOwner {
        uint256 old = storedValue;
        storedValue  = 0;
        updateCount += 1;
        emit ValueChanged(msg.sender, old, 0);
    }

    function get() public view returns (uint256) {
        return storedValue;
    }

    function getInfo() public view returns (
        address _owner,
        uint256 _value,
        uint256 _updateCount
    ) {
        return (owner, storedValue, updateCount);
    }
}
