# Reproducibility Guide

## A. Smart contract

```bash
npm install
npx hardhat compile
npx hardhat test
```

Expected test coverage includes:
- grant consent by the patient;
- access by an authorized requestor;
- patient revocation;
- isolation of patient consent records.

## B. Sepolia deployment

Create `.env` from `.env.example` and provide a Sepolia RPC endpoint plus a funded testnet private key.

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

Save the printed contract address and transaction hash in the experiment log.

## C. Static analysis

```bash
pip install slither-analyzer
slither .
```

For each run record:
- git commit hash;
- Solidity compiler version;
- Slither version;
- network and deployment address;
- warnings/errors and whether they were fixed.

## D. Python environment

```bash
pip install -r requirements.txt
```

Run the preprocessing, benchmark, calibration, and SHAP scripts using the dataset locations documented in their source code.

## E. Reproducibility principle

Reported experimental values should always be tied to a commit, environment, dataset version, and run configuration. The repository therefore distinguishes source implementation from manuscript-reported experimental results.
