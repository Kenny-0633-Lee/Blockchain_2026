// hardhat.config.js
// dotenv를 require하면 .env 파일을 OS 무관하게 자동 로드합니다.
// Windows PowerShell에서 "source .env" 불필요 — 이 한 줄이 대신합니다.
require("dotenv").config();
require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.20",
  networks: {
    // 로컬 Hardhat 네트워크 (기본)
    hardhat: {
      chainId: 31337,
    },
    // Sepolia 배포 (.env 파일에서 자동 로드 — OS 무관)
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "https://rpc.sepolia.org",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 11155111,
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY || "",
  },
};
