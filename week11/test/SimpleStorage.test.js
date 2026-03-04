/**
 * week11/test/SimpleStorage.test.js
 * Hardhat + Mocha + Chai 단위 테스트
 *
 * 실행:
 *   npx hardhat test
 *   npx hardhat test --verbose
 */

const { expect }        = require("chai");
const { ethers }        = require("hardhat");
const { loadFixture }   = require("@nomicfoundation/hardhat-toolbox/network-helpers");

// ── 픽스처: 각 테스트 전 초기 상태 배포 ──────────────────────────────────────
async function deploySimpleStorageFixture() {
    const [owner, alice, bob] = await ethers.getSigners();

    const SimpleStorage = await ethers.getContractFactory("SimpleStorage");
    const contract      = await SimpleStorage.deploy(0n);   // 초기값 0
    await contract.waitForDeployment();

    return { contract, owner, alice, bob };
}

// ── 테스트 스위트 ─────────────────────────────────────────────────────────────
describe("SimpleStorage", function () {

    // ── 배포 ────────────────────────────────────────────────────────────────
    describe("배포 (Deployment)", function () {

        it("배포자가 owner로 설정되어야 한다", async function () {
            const { contract, owner } = await loadFixture(deploySimpleStorageFixture);
            expect(await contract.owner()).to.equal(owner.address);
        });

        it("초기 storedValue가 0이어야 한다", async function () {
            const { contract } = await loadFixture(deploySimpleStorageFixture);
            expect(await contract.get()).to.equal(0n);
        });

        it("초기 updateCount가 0이어야 한다", async function () {
            const { contract } = await loadFixture(deploySimpleStorageFixture);
            expect(await contract.updateCount()).to.equal(0n);
        });
    });

    // ── set() 함수 ──────────────────────────────────────────────────────────
    describe("set()", function () {

        it("값을 저장하고 get()으로 읽을 수 있어야 한다", async function () {
            const { contract } = await loadFixture(deploySimpleStorageFixture);
            await contract.set(42n);
            expect(await contract.get()).to.equal(42n);
        });

        it("set() 호출 시 updateCount가 증가해야 한다", async function () {
            const { contract } = await loadFixture(deploySimpleStorageFixture);
            await contract.set(10n);
            await contract.set(20n);
            expect(await contract.updateCount()).to.equal(2n);
        });

        it("누구나 set()을 호출할 수 있어야 한다", async function () {
            const { contract, alice } = await loadFixture(deploySimpleStorageFixture);
            await contract.connect(alice).set(99n);
            expect(await contract.get()).to.equal(99n);
        });

        it("set() 호출 시 ValueChanged 이벤트가 발생해야 한다", async function () {
            const { contract, owner } = await loadFixture(deploySimpleStorageFixture);
            await expect(contract.set(42n))
                .to.emit(contract, "ValueChanged")
                .withArgs(owner.address, 0n, 42n);
        });

        it("ValueChanged 이벤트에 oldValue와 newValue가 정확해야 한다", async function () {
            const { contract, alice } = await loadFixture(deploySimpleStorageFixture);
            await contract.set(10n);
            await expect(contract.connect(alice).set(20n))
                .to.emit(contract, "ValueChanged")
                .withArgs(alice.address, 10n, 20n);
        });
    });

    // ── reset() 함수 ────────────────────────────────────────────────────────
    describe("reset()", function () {

        it("owner가 reset()을 호출하면 0이 되어야 한다", async function () {
            const { contract } = await loadFixture(deploySimpleStorageFixture);
            await contract.set(100n);
            await contract.reset();
            expect(await contract.get()).to.equal(0n);
        });

        it("owner가 아니면 reset()이 실패해야 한다 (Unauthorized)", async function () {
            const { contract, alice } = await loadFixture(deploySimpleStorageFixture);
            await contract.set(100n);
            await expect(contract.connect(alice).reset())
                .to.be.revertedWithCustomError(contract, "Unauthorized");
        });
    });

    // ── getInfo() 함수 ──────────────────────────────────────────────────────
    describe("getInfo()", function () {

        it("owner, value, updateCount를 모두 반환해야 한다", async function () {
            const { contract, owner } = await loadFixture(deploySimpleStorageFixture);
            await contract.set(77n);

            const [_owner, _value, _count] = await contract.getInfo();
            expect(_owner).to.equal(owner.address);
            expect(_value).to.equal(77n);
            expect(_count).to.equal(1n);
        });
    });

    // ── Gas 확인 ───────────────────────────────────────────────────────────
    describe("Gas 소비", function () {

        it("get()은 외부 트랜잭션 없이 호출 가능 (view 함수)", async function () {
            const { contract } = await loadFixture(deploySimpleStorageFixture);
            // view 함수는 트랜잭션 없이 정적 호출
            const value = await contract.get.staticCall();
            expect(value).to.equal(0n);
        });

        it("set()은 Gas를 소비하는 트랜잭션이어야 한다", async function () {
            const { contract } = await loadFixture(deploySimpleStorageFixture);
            const tx = await contract.set(1n);
            const receipt = await tx.wait();
            // 21,000 (기본) + 연산비용 > 0
            expect(receipt.gasUsed).to.be.greaterThan(0n);
        });
    });
});
