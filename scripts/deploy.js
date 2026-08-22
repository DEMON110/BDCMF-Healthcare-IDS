const hre = require("hardhat");

async function main() {
  const Factory = await hre.ethers.getContractFactory("ConsentRegistry");
  const registry = await Factory.deploy();
  await registry.waitForDeployment();
  const address = await registry.getAddress();
  console.log(`ConsentRegistry deployed to: ${address}`);
  console.log(`Network: ${hre.network.name}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
