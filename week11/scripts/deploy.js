const hre = require("hardhat");

async function main() {
  const ONE_YEAR = 365 * 24 * 60 * 60;
  const unlockTime = Math.floor(Date.now() / 1000) + ONE_YEAR;
  const lockedAmount = hre.ethers.parseEther("0.001");

  console.log("Deploying Lock contract...");
  console.log(`  Unlock time : ${new Date(unlockTime * 1000).toLocaleString()}`);
  console.log(`  Locked amount: 0.001 ETH`);

  const Lock = await hre.ethers.getContractFactory("Lock");
  const lock = await Lock.deploy(unlockTime, { value: lockedAmount });

  await lock.waitForDeployment();

  const address = await lock.getAddress();
  console.log(`\n✅ Lock deployed to: ${address}`);
  console.log(`   Etherscan: https://sepolia.etherscan.io/address/${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
