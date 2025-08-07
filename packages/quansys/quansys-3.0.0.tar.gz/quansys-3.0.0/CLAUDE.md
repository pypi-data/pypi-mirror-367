# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Prerequisites and Installation

- **ANSYS Electronics Desktop 2024 R2** required for .aedt file operations
- Install via: `git clone https://github.com/hutorihunzu/quansys.git && pip install -e ./quansys`
- License availability may affect testing (LicenseUnavailableError handling in tests)
- Windows 10/11 or Linux workstation capable of running HFSS in non-graphical mode

## Development Commands

### Getting Started
- Copy example files: `quansys example --type simple` (basic) or `quansys example --type complex` (advanced)
- Copy AEDT only: `quansys example --no-config`
- List available examples: `quansys example --list`

### Testing
- Run all tests: `pytest`
- Run tests with verbose output: `pytest -v`
- Run specific test file: `pytest tests/test_eigenmode.py`
- Run tests with notebook execution: `pytest --nbmake` (requires nbmake dependency)

### Linting and Code Quality
- Run linter: `ruff check`
- Auto-fix linting issues: `ruff check --fix`
- Format code: `ruff format`

### Documentation
- Serve documentation locally: `./serve-docs.sh` or `mkdocs serve`
- Build documentation: `mkdocs build`

### CLI Usage
- Main CLI entry point: `quansys` (installed via `pip install .`)
- Run workflow locally: `quansys run <config.yaml>`
- Submit cluster job: `quansys submit <config.yaml> <venv_name> --name <project_name> --mem <MB> --timeout <HH:MM>`
- Prepare job without submission: `quansys submit <config.yaml> <venv_name> --name <project_name> --prepare`
- Overwrite existing project: `quansys submit <config.yaml> <venv_name> --name <project_name> --overwrite`

## Architecture Overview

### Core Modules

**Simulation Module** (`src/quansys/simulation/`):
- `EigenmodeAnalysis`: HFSS eigenmode simulations with customizable setup parameters
- `QuantumEPR`: Energy participation ratio analysis for quantum parameter extraction
- `DriveModelAnalysis`: Driven model analysis capabilities
- Support for both classical HFSS simulations and quantum analysis workflows

**Workflow Module** (`src/quansys/workflow/`):
- `execute_workflow`: Main workflow execution engine
- `WorkflowConfig`: Configuration management for simulation workflows
- **Builder System**: Three types of builders for automated parameter sweeps:
  - `DesignVariableBuilder`: Manages HFSS design variables
  - `FunctionBuilder`: Executes custom Python functions during workflows
  - `ModuleBuilder`: Loads and executes external Python modules
- `PyaedtFileParameters`: Session management for AEDT file operations

**CLI Module** (`src/quansys/cli/`):
- Built with Typer for command-line interface
- Supports cluster job submission and local execution
- Includes example file management and project preparation

### Workflow Execution Model

Workflows follow a **4-phase process** that repeats for each unique parameter combination:

1. **Prepare**: Create iteration folder, copy template .aedt file
2. **Build**: Apply parameter changes using builders (DesignVariableBuilder, FunctionBuilder, ModuleBuilder)  
3. **Simulate**: Execute simulation analyses (EigenmodeAnalysis, QuantumEPR, etc.)
4. **Aggregate**: Flatten results to CSV files for analysis

**Folder Structure**:
```
results/
├─ iterations/
│  ├─ 000/  # first parameter set
│  │  ├─ build.aedt
│  │  ├─ build_parameters.json
│  │  └─ [simulation_results].json
│  └─ 001/  # second parameter set
└─ aggregations/
   └─ [aggregation_name].csv
```

**Important**: Reserved identifiers `"build"` and `"prepare"` cannot be used as simulation names.

### Key Design Patterns

**Type-Safe Configuration**: Uses Pydantic models with discriminated unions for type safety across simulation types and builders.

**Modular Builder Pattern**: The workflow system uses a builder pattern where `SUPPORTED_BUILDERS` can be mixed and matched in configuration files to create complex parameter sweep workflows.

**Session Management**: `PyaedtFileParameters` provides context manager pattern for AEDT file operations with automatic cleanup and license management.

**Analysis Chain**: Simulations follow a consistent pattern: configuration → analysis → results, with type-safe result objects for each simulation type.

**YAML Configuration Management**: Workflows support round-trip YAML serialization via `cfg.save_to_yaml()` and `WorkflowConfig.load_from_yaml()` for configuration persistence and sharing.

## Dependencies and Environment

- Python 3.11+ required
- Primary dependencies: `pyaedt[all]`, `qutip`, `pint`, `h5py`, `pandas`, `pydantic_yaml`, `typer`
- Optional dependencies for docs: `mkdocs`, `mkdocs-material`
- Testing: `pytest`, `nbmake` for notebook testing
- Linting: `ruff` (configured in pyproject.toml optional dependencies)

## Development Notes

### Session Management
- Use `non_graphical=True` in `PyaedtFileParameters` for headless HFSS operations (essential for testing and cluster runs)
- License availability can block testing - tests use `pytest.skip()` when licenses unavailable

### Parameter Sweeps
- Use `pycaddy.sweeper.DictSweep` for parameter sweep configurations
- Workflow engine hashes parameter combinations to enable resumable execution
- Each unique parameter set gets assigned a zero-padded UID folder (000, 001, etc.)

### Simulation Limitations
- **QuantumEPR**: Limited to 3 modes per analysis instance (create multiple instances for more modes)
- **Mode labeling**: Use `ModesToLabels` with `ManualInference` and `OrderInference` for automatic mode assignment

### Configuration Management
- YAML files can be hand-edited between Python workflow definitions
- Use `WorkflowConfig.load_from_yaml()` and `cfg.save_to_yaml()` for persistence
- Keep separate config files for different designs or sweep types

## Project Structure Notes

- Package source in `src/quansys/` following modern Python packaging standards
- Test resources in `tests/resources/` with AEDT design files
- Examples in `src/quansys/examples/` with both simple and complex configurations
- Documentation uses MkDocs with API documentation in `docs/api/`
- Results directory structure supports iterative workflows with metadata tracking

## Recent Development Changes

For detailed information about recent performance optimizations and documentation improvements, see [SESSION_SUMMARY.md](SESSION_SUMMARY.md). Key highlights include:

- **CLI Performance**: 93% improvement (3.96s → 0.28s startup time) through lazy loading architecture
- **Documentation Restructure**: Simplified terminal guide, reorganized ModesToLabels documentation with practical examples
- **Label Conventions**: Standardized quantum mode labeling (readout, purcell, control) with clear quality factor patterns