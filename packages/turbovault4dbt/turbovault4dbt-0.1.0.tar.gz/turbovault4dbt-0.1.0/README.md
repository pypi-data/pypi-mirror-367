# TurboVault4dbt_cli

![TurboVault4dbt Banner](https://user-images.githubusercontent.com/81677440/214857459-13fb4674-06e7-40d1-abb6-1b43133f2f8b.png)

---

## What is TurboVault4dbt_cli?
TurboVault4dbt_cli is an open-source CLI tool that automatically generates dbt models according to [datavault4dbt](https://github.com/ScalefreeCOM/datavault4dbt) templates. It uses a metadata input of your Data Vault 2.0 from one of the supported databases and creates ready-to-process dbt-models.

---

## Prerequisites
- Python 3.8+
- Metadata analysis done and stored in a supported format (see below)
- [dbt project](https://docs.getdbt.com/docs/get-started/getting-started-dbt-core)
- [datavault4dbt](https://github.com/ScalefreeCOM/datavault4dbt) dbt package

---

## Supported Metadata Sources
- **Snowflake**
- **BigQuery**
- **Google Sheets**
- **Excel**
- **SQLite DB Files**

---

## How does my metadata needs to look like?
Your metadata needs to be stored in the following tables/worksheets: 
- [Source Data](https://github.com/ScalefreeCOM/turbovault4dbt/wiki/source-data)
- [Standard Hubs](https://github.com/ScalefreeCOM/turbovault4dbt/wiki/hubs)
- [Standard Links](https://github.com/ScalefreeCOM/turbovault4dbt/wiki/links)
- [Non-Historized Links](https://github.com/ScalefreeCOM/turbovault4dbt/wiki/non-Historized-links)
- [Standard Satellites](https://github.com/ScalefreeCOM/turbovault4dbt/wiki/standard-satellites)
- [Non-Historized Satellites](https://github.com/ScalefreeCOM/turbovault4dbt/wiki/non-Historized-satellites)
- [Multi-Active Satellites](https://github.com/ScalefreeCOM/turbovault4dbt/wiki/multiactive-satellites)
- [Point-In-Time Tables](https://github.com/ScalefreeCOM/turbovault4dbt/wiki/Point-In-Time)
- [Reference Tables](https://github.com/ScalefreeCOM/turbovault4dbt/wiki/reference-tables)
---

## Installation (CLI Version)

1. Clone this repository:
   ```sh
   git clone https://github.com/ScalefreeCOM/turbovault4dbt.git
   cd turbovault4dbt
   ```
2. (Recommended) Create and activate a virtual environment:
   ```sh
   python3 -m venv turbovault-env
   source turbovault-env/bin/activate
   ```
3. Install in editable mode:
   ```sh
   pip install -e .
   ```

---

## Quickstart: Using the CLI

### 1. Prepare your metadata
- See [metadata_ddl/](metadata_ddl/) for DDL scripts and Excel templates.
- Configure your metadata connection in `src/turbovault4dbt/backend/config/config.ini`.

### 2. Run TurboVault4dbt_cli

#### Basic usage:
```sh
# List available nodes from your metadata Excel file
$ turbovault list --file path/to/your.xlsx

# Generate dbt models for selected nodes
$ turbovault run --file path/to/your.xlsx -s hub1

# Use selectors (e.g., +node, node+, @node)
$ turbovault run --file path/to/your.xlsx -s '+sat1 hub2+ @masat3'

# Specify output directory
$ turbovault run --file path/to/your.xlsx --output-dir my_output_dir -s hub1
```

#### Command reference:
- `turbovault run --file <input.xlsx> [-s <selector>] [--output-dir <dir>]`  
  Generate dbt models for selected nodes.
- `turbovault list --file <input.xlsx> [-s <selector>]`  
  List resolved nodes for a selector (dry run).

#### Selector syntax:
- `A+` — node A and all descendants
- `+A` — node A and all ancestors
- `@A` — node A, all ancestors, and all descendants
- Multiple selectors can be space-separated

---

## Regression Testing

To run the regression test suite:
```sh
pip install -r requirements-test.txt
pytest tests/test_regression.py
```
- Add new test cases by creating folders in `tests/` with `input.xlsx` and `expected_output/`.
- Negative test cases (expected failures) are also supported.

---

## Project Structure
- `src/turbovault4dbt/` — all source code
- `tests/` — regression test cases
- `pyproject.toml`, `requirements.txt`, etc. — project config in root

---

## Releases
See [GitHub Releases](https://github.com/ScalefreeCOM/turbovault4dbt/releases)

---

## License
See [LICENSE](LICENSE)

---

## Need Help?
- [Open an issue](https://github.com/ScalefreeCOM/turbovault4dbt/issues)
- [Wiki](https://github.com/ScalefreeCOM/turbovault4dbt/wiki)
