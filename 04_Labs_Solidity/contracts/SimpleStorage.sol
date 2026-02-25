// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26; // 2026년 기준 최신 버전 가정 (0.8.x)

// Lecture: Blockchain 2026
// Week 05: Introduction to Smart Contracts
contract SimpleStorage {
    
    // 1. State Variable (블록체인에 영구 저장되는 변수)
    uint256 private storedData;

    // 2. Event (값 변경 시 로그 남기기)
    event DataChanged(uint256 oldValue, uint256 newValue);

    // 3. Setter Function (가스비 발생 O)
    // 데이터를 블록체인에 씁니다.
    function set(uint256 x) public {
        emit DataChanged(storedData, x);
        storedData = x;
    }

    // 4. Getter Function (가스비 발생 X - view)
    // 블록체인에서 데이터를 읽기만 합니다.
    function get() public view returns (uint256) {
        return storedData;
    }
}