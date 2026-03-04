/**
 * week11/scripts/deploy.js
 * ========================
 * Lock 컨트랙트 배포 스크립트
 *
 * 실행:
 *   npx hardhat run scripts/deploy.js --network localhost
 *   npx hardhat run scripts/deploy.js --network sepolia
 */

const { ethers } = require("hardhat");

async function main() {
  // 1분 후 잠금 해제 (로컬 테스트용)
  const ONE_MINUTE_IN_SECS = 60;
  const unlockTime = Math.floor(Date.now() / 1000) + ONE_MINUTE_IN_SECS;

  // 배포 시 0.001 ETH 입금
  const lockedAmount = ethers.parseEther("0.001");

  console.log("🚀 Lock 컨트랙트 배포 중...");
  console.log(`  잠금 해제 시각: ${new Date(unlockTime * 1000).toLocaleString()}`);
  console.log(`  잠금 금액: ${ethers.formatEther(lockedAmount)} ETH`);

  const lock = await ethers.deployContract("Lock", [unlockTime], {
    value: lockedAmount,
  });

  await lock.waitForDeployment();

  console.log(`\n✅ 배포 완료!`);
  console.log(`   컨트랙트 주소: ${await lock.getAddress()}`);
  console.log(`   네트워크: ${hre.network.name}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
