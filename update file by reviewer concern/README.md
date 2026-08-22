# BDCMF-Healthcare-IDS / BECF Reproducibility Package

This repository contains the implementation artifacts for the **Blockchain-Enabled Cybersecurity Framework (BECF)** described in the accompanying manuscript. It combines:

1. healthcare-IoT intrusion detection on ToN-IoT;
2. blockchain transaction anomaly detection on Elliptic;
3. probability calibration and SHAP explainability;
4. a Solidity consent-management smart contract for Ethereum-compatible networks; and
5. deployment and reproducibility utilities.

## Repository structure

```text
BDCMF-Healthcare-IDS/
├── contracts/
│   └── ConsentRegistry.sol          # Solidity consent-management contract
├── scripts/
│   └── deploy.js                    # Hardhat deployment script
├── test/
│   └── ConsentRegistry.test.js      # Smart-contract unit tests
├── docs/
│   └── REPRODUCIBILITY.md          # Step-by-step reproduction guide
├── results/
│   └── tables/                      # Generated evaluation tables
├── baseline_benchmark.py            # ML benchmark pipeline
├── calibrate_and_bootstrap.py       # Calibration/statistical evaluation
├── preprocess_elliptic.py           # Elliptic preprocessing
├── preprocess_toniot.py             # ToN-IoT preprocessing
├── shap_explain.py                  # SHAP explanations
├── deploy_sepolia.py                # Optional Python/Web3 deployment utility
├── requirements.txt                 # Python dependencies
├── package.json                     # Solidity/Hardhat dependencies
├── hardhat.config.js                # Hardhat configuration
├── .env.example                     # Environment-variable template
├── SECURITY_AUDIT.md                # Smart-contract audit instructions
└── LICENSE
```

## What was added in response to reproducibility review

The original repository contained the Python analysis scripts but did not expose the Solidity source or a sufficiently detailed user manual. The smart-contract implementation is now explicitly included under `contracts/`, together with a Hardhat project, deployment script, tests, and audit instructions.

## Smart contract implementation

`contracts/ConsentRegistry.sol` implements the consent-management finite-state machine described in the manuscript:

- `NONE`
- `GRANTED`
- `REVOKED`
- `EXPIRED`

The public operations are:

- `grantConsent(requestor, scope, expiry)` — patient grants access;
- `revokeConsent(requestor, scope)` — patient revokes access;
- `accessData(patient, scope)` — requestor checks and records authorized access;
- `checkExpiry(patient, requestor, scope)` — updates an expired consent;
- `getConsent(patient, requestor, scope)` — reads consent metadata.

The contract stores consent metadata only. It does **not** store patient medical records on-chain.

The implementation also emits `ConsentGranted`, `ConsentRevoked`, `ConsentExpired`, and `DataAccessed` events to provide an auditable event trail.

## Requirements

### Python

Python 3.10+ is recommended. Install the packages with:

```bash
pip install -r requirements.txt
```

### Solidity / Hardhat

Node.js 18+ is recommended.

```bash
npm install
```

## 1. Compile the smart contract

```bash
npx hardhat compile
```

Successful compilation produces the contract artifacts under `artifacts/`.

## 2. Run smart-contract tests

```bash
npx hardhat test
```

The tests exercise grant, access, revocation, and consent-record isolation behavior.

## 3. Run static security analysis

Install Slither:

```bash
pip install slither-analyzer
```

Then run:

```bash
slither .
```

See `SECURITY_AUDIT.md` for the audit checklist and reproducibility notes.

## 4. Deploy to Ethereum Sepolia

**Never commit a private key. Use a dedicated testnet account.**

Copy the environment template:

```bash
cp .env.example .env
```

Set `SEPOLIA_RPC` and `PRIVATE_KEY` in `.env`, then run:

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

The deployment script prints the deployed `ConsentRegistry` address.

### Python/Web3 deployment utility

The repository also retains `deploy_sepolia.py` for users who prefer Python/Web3. It is an auxiliary deployment/measurement utility; the canonical Solidity build and deployment path is the Hardhat workflow above.

## 5. Consent lifecycle example

A typical lifecycle is:

```text
NONE
  │
  │ grantConsent()
  ▼
GRANTED ───────────────► REVOKED
  │                        ▲
  │ expiry reached         │ revokeConsent()
  ▼                        │
EXPIRED                    │
```

`accessData()` is permitted only while the consent is `GRANTED` and the current block timestamp is before the expiry time.

## 6. Reproducing the machine-learning pipeline

The Python scripts correspond to the two detection layers described in the manuscript:

### ToN-IoT network IDS

```bash
python preprocess_toniot.py
python baseline_benchmark.py
```

### Elliptic blockchain anomaly detection

```bash
python preprocess_elliptic.py
python baseline_benchmark.py
```

### Calibration and statistical evaluation

```bash
python calibrate_and_bootstrap.py
```

### SHAP explanations

```bash
python shap_explain.py
```

Dataset files are not redistributed in this repository. Obtain them from their permitted public sources and place them in the paths expected by the preprocessing scripts.

## 7. Relationship to the manuscript

The repository exposes the implementation corresponding to the manuscript's smart-contract design: identity binding through Ethereum addresses, consent scopes, expiry, patient-controlled grant/revoke operations, immutable event logging, and pre-access authorization checks.

The manuscript reports the following smart-contract evaluation figures: `grantConsent` 48,500 ± 1,250 gas, `revokeConsent` 35,200 ± 980 gas, `batchGrant(x10)` 398,500 ± 8,200 gas, and a reported 99.8% success rate for `grantConsent`. These numbers are experimental results reported by the manuscript and should be reproduced using the exact deployment configuration and test data rather than assumed from the source code alone.

## 8. Security and privacy

- Do not place patient-identifiable information on-chain.
- Do not commit private keys, RPC credentials, API keys, or `.env` files.
- Use Sepolia for reproduction unless production deployment has been separately authorized.
- Run static analysis and unit tests before deployment.
- Treat static-analysis tools as complementary evidence, not as a formal guarantee of absence of vulnerabilities.

## 9. Citation and reproducibility

For an independent review, the recommended sequence is:

1. clone/download this repository;
2. install Python and Node.js dependencies;
3. compile `contracts/ConsentRegistry.sol`;
4. execute `npx hardhat test`;
5. run Slither and record its output;
6. optionally deploy to Sepolia using a dedicated testnet account;
7. reproduce the ML preprocessing and evaluation using the permitted datasets.

This structure is intended to make the smart-contract implementation directly inspectable instead of requiring the reviewer to infer its existence from the manuscript.
