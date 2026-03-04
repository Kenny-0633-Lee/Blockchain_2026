/**
 * week11/test/Lock.test.js
 * ========================
 * Lock 컨트랙트 자동화 테스트
 *
 * 실행:
 *   npx hardhat test
 *   npx hardhat test --grep "withdraw"  # 특정 테스트만
 */

const { expect } = require("chai");
const { ethers }  = require("hardhat");
const { time, loadFixture } = require("@nomicfoundation/hardhat-toolbox/network-helpers");

describe("Lock", function () {
  // ── 픽스처: 공통 초기 상태 설정 ──
  async function deployFixture() {
    const ONE_YEAR = 365 * 24 * 60 * 60;
    const unlockTime   = (await time.latest()) + ONE_YEAR;
    const lockedAmount = ethers.parseEther("1.0");

    const [owner, otherAccount] = await ethers.getSigners();

    const Lock = await ethers.getContractFactory("Lock");
    const lock = await Lock.deploy(unlockTime, { value: lockedAmount });

    return { lock, unlockTime, lockedAmount, owner, otherAccount };
  }

  // ── 배포 테스트 ──
  describe("배포", function () {
    it("올바른 잠금 해제 시각 설정", async function () {
      const { lock, unlockTime } = await loadFixture(deployFixture);
      expect(await lock.unlockTime()).to.equal(unlockTime);
    });

    it("소유자 주소 올바르게 설정", async function () {
      const { lock, owner } = await loadFixture(deployFixture);
      expect(await lock.owner()).to.equal(owner.address);
    });

    it("컨트랙트에 ETH 입금 확인", async function () {
      const { lock, lockedAmount } = await loadFixture(deployFixture);
      const balance = await ethers.provider.getBalance(await lock.getAddress());
      expect(balance).to.equal(lockedAmount);
    });

    it("과거 시간으로 배포 시 실패", async function () {
      const pastTime = (await time.latest()) - 1;
      const Lock = await ethers.getContractFactory("Lock");
      await expect(
        Lock.deploy(pastTime, { value: ethers.parseEther("1") })
      ).to.be.revertedWith("Unlock time should be in the future");
    });
  });

  // ── 인출 테스트 ──
  describe("인출(withdraw)", function () {
    it("잠금 시간 전 인출 시 실패", async function () {
      const { lock } = await loadFixture(deployFixture);
      await expect(lock.withdraw()).to.be.revertedWith("You can't withdraw yet");
    });

    it("소유자 아닌 계정으로 인출 시 실패", async function () {
      const { lock, unlockTime, otherAccount } = await loadFixture(deployFixture);
      await time.increaseTo(unlockTime);
      await expect(lock.connect(otherAccount).withdraw())
        .to.be.revertedWith("You aren't the owner");
    });

    it("잠금 시간 후 소유자 인출 성공", async function () {
      const { lock, unlockTime, lockedAmount, owner } = await loadFixture(deployFixture);
      await time.increaseTo(unlockTime);

      await expect(lock.withdraw()).to.changeEtherBalances(
        [owner, lock],
        [lockedAmount, -lockedAmount]
      );
    });

    it("인출 시 Withdrawal 이벤트 발생", async function () {
      const { lock, unlockTime, lockedAmount } = await loadFixture(deployFixture);
      await time.increaseTo(unlockTime);
      await expect(lock.withdraw())
        .to.emit(lock, "Withdrawal")
        .withArgs(lockedAmount, await time.latest());
    });
  });
});
