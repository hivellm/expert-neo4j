# Scripts Directory

This directory contains all utility scripts for the expert-neo4j project, except for `compare.py` and `preprocess.py` which remain in the root directory.

## Scripts Overview

### Testing Scripts
- `run_single_test.py` - Run individual tests via CLI and update checklist
- `test_version_cli.py` - Comprehensive CLI testing for expert versions
- `test_limitations_cli.py` - Test known limitations via CLI
- `test_checkpoint_250.py` - Test specific checkpoint
- `test_gpu.py` - GPU testing utilities

### Analysis Scripts
- `analyze_test_results.py` - Analyze test results and generate validation reports
- `analyze_checkpoint_results.py` - Analyze checkpoint comparison results
- `analyze_checkpoint_250.py` - Analyze checkpoint 250 specifically
- `analyze_checkpoint_quality.py` - Analyze checkpoint quality metrics
- `analyze_final_checkpoints.py` - Analyze final training checkpoints
- `analyze_cypher_distribution.py` - Analyze Cypher query distribution
- `analyze_command_distribution.py` - Analyze command distribution in dataset
- `analyze_dataset_sources.py` - Analyze dataset sources
- `analyze_additional_datasets.py` - Analyze additional datasets

### Dataset Scripts
- `check_dataset.py` - Check dataset integrity
- `check_dataset_status.py` - Check dataset status
- `check_format.py` - Check dataset format
- `check_sql_in_dataset.py` - Check for SQL queries in dataset
- `check_synthetic_consistency.py` - Check synthetic data consistency
- `check_reasoning.py` - Check for reasoning blocks in dataset
- `verify_dataset.py` - Verify dataset validity
- `integrate_cypherbench.py` - Integrate CypherBench dataset

### Comparison Scripts
- `compare_versions.py` - Compare different expert versions
- `run_cli_comparison.py` - Run CLI-based version comparisons
- `check_test12.py` - Check specific test case

### Documentation Scripts
- `collect_documentation.py` - Collect documentation from sources
- `run_documentation_collection.ps1` - PowerShell script for documentation collection
- `generate_distribution_charts.py` - Generate distribution charts

### Utility Scripts
- `test_cli.bat` - Batch script for CLI testing
- `test_gpu.bat` - Batch script for GPU testing

## Usage

All scripts should be run from the expert-neo4j root directory:

```bash
# Example: Run a single test
python scripts/run_single_test.py match_001

# Example: Analyze test results
python scripts/analyze_test_results.py version_0.2.3_cli_results.json
```

## Path References

Scripts use relative paths:
- CLI path: `../../cli/target/release/expert-cli.exe`
- Base model: `../../models/Qwen3-0.6B`
- Checklist file: `../test_checklist.json`

