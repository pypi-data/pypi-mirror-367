# Changelog


---

## [Unreleased]
### Added
- Multi-model parallel sampling (f.e. for parameter tuning jobs, etc.)

---
## [0.1.25]
### Fixed
- Start of global refactoring

## [0.1.24]
### Fixed
- Bugfix native circuit execution

## [0.1.23]
### Added
- Support for quantum algorithm v2

## [0.1.22]
### Fixed
- Bugfix

## [0.1.21]
### Added
- Native q.node support for `shots`

## [0.1.20]
### Fixed
- Circuit bug fix

## [0.1.19]
### Added
- Support for Dynex Quantum nodes: new parameters `cluster_type` (default `1`) and `is_cluster` (default `True`)
- Energy ground state display: now showing underlying model energy

## [0.1.18]
### Added
- Native support for PennyLane gate-based circuits
- Native support for OpenQASM gate-based circuits
- Native support for Qiskit gate-based circuits

## [0.1.17]
### Added
- Native support for Discrete Quadratic Models (DQM)
### Fixed
- Return sampleset format of CQM models by inverting to original CQM

## [0.1.16]
### Added
- Dynex cluster support

## [0.1.15]
### Added
- Support for subscription model
- Support for `n.quantum` gates and qubits
### Changed
- Updated terminology from "chips" to "circuits"
- Fixed elapsed time display bug
- Minor typo fixes

## [0.1.14]
### Fixed
- Small testnet sampling bugfix

## [0.1.13]
### Added
- `dynex.estimate_costs()` function
### Fixed
- Sampling of model type `sat`

## [0.1.12]
### Added
- Compression of compute file for mainnet sampling

## [0.1.11]
### Added
- Official Dynex marketplace version
- Billing functionality
- File upload / encryption / data handling (server side)
- API layer & AWS Elastic Cloud support
- Validation clauses
- Progress % and step display during compute
- New DNX encryption format
### Changed
- Updated `dynex.ini` for marketplace compatibility
- Using SDK API application layer
- Removed file upload progress bar
- Changed display refresh interval from 2 → 5 seconds

## [0.1.10]
### Fixed
- `np.float64` conversion bug

## [0.1.9]
### Added
- Energy ground state calculation moved into `_DynexSampler` class
- `debugging=True` option for sampling
- New parameter: `bnb=True/False` (testnet only, branch-and-bound method)
- `dynex.sample(bqm, **parameters)`
- `dynex.sample_qubo(Q, offset, **parameters)`
- `dynex.sample_ising(h, j, **parameters)`
### Improved
- `bqm2bin` function:
  - Faster: direct conversion from BQM (skipped QUBO step)
  - Rydberg Hamiltonian formulation
  - Reduction of linear terms

## [0.1.8]
### Added
- Accuracy improvement: validate solution file energies with voltages and omit incorrect reads
- Improved sampling display (showing ground state, decluttered)
- Default `logging=False` for CQM/BQM/SAT models

## [0.1.7]
### Changed
- All internal functions renamed with `_x` prefix
- Don't raise exception on missing `.ini`, issue warning instead (fix for `import dynex`)
- Testnet: auto-use max fitting circuits, ignore `num_reads`
- Temporarily removed "boost job priority"
