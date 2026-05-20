// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract SimpleStorage {
    uint256 private storedValue;
    address public owner;

    event ValueChanged(address indexed by, uint256 newValue);

    constructor() {
        owner = msg.sender;
    }

    function set(uint256 value) public {
        storedValue = value;
        emit ValueChanged(msg.sender, value);
    }

    function get() public view returns (uint256) {
        return storedValue;
    }
}
