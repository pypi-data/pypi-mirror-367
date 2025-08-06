# TurboVault4dbt_cli

![TurboVault4dbt Banner](https://user-images.githubusercontent.com/81677440/214857459-13fb4674-06e7-40d1-abb6-1b43133f2f8b.png)

---

## What is TurboVault4dbt_cli?
TurboVault4dbt_cli is an open-source CLI tool that automatically generates dbt models according to [datavault4dbt](https://github.com/ScalefreeCOM/datavault4dbt) templates. It uses a metadata input of your Data Vault 2.0 from one of the supported databases and creates ready-to-process dbt-models.

---

## Prerequisites
- Python 3.8+
- Metadata prepared in one of the supported formats (see below)
- [dbt project](https://docs.getdbt.com/docs/get-started/getting-started-dbt-core)
- [datavault4dbt](https://github.com/ScalefreeCOM/datavault4dbt) dbt package


---

## Supported Metadata Formats  
- **Excel files:** `.xls`, `.xlsx`
- **CSV files:** folder of CSVs (one per sheet/table)

---

## How does my metadata need to look like?
Your metadata needs to be stored in the following tables/worksheets/files: 
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

## Installation

You can install TurboVault4dbt_cli directly from PyPI:
```sh
pip install turbovault4dbt
```
Or install from source for development:
```sh
git clone https://github.com/ScalefreeCOM/turbovault4dbt.git
cd turbovault4dbt
pip install -e .
```

---

## Publishing to PyPI

1. **Build the package (inside your project directory):**
    ```sh
    python -m build
    ```

2. **Upload to PyPI using Twine:**
    ```sh
    pip install twine  # if not already installed
    twine upload dist/*
    ```

3. **(Optional) Test upload to TestPyPI first:**
    ```sh
    twine upload --repository testpypi dist/*
    ```

4. **After upload, install your package from PyPI:**
    ```sh
    pip install turbovault4dbt
    ```

For more details, see the [official Python packaging docs](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

---

## Quickstart: Using the CLI

### 1. Prepare your metadata
- Prepare your metadata as Excel (`.xls` or `.xlsx`) or as a folder of CSV files (one CSV per sheet/table, filenames matching required sheets).
- (See [metadata_ddl/](metadata_ddl/) for example templates.)

### 2. Run TurboVault4dbt_cli

#### Basic usage:
```sh
# List all nodes in your metadata (Excel or CSV)
turbovault list -f xlsx path/to/your.xlsx
turbovault list -f csv path/to/your_csv_folder

# Generate dbt models for all nodes
turbovault run -f xlsx path/to/your.xlsx
turbovault run -f csv path/to/your_csv_folder

# Generate dbt models for selected nodes
turbovault run -f xlsx path/to/your.xlsx -s hub1 link1 sat1
turbovault run -f csv path/to/your_csv_folder -s '+hub1' '@sat1'

# Specify output directory
turbovault run -f xlsx path/to/your.xlsx --output-dir my_output_dir
```
#### Command reference:
- `turbovault run -f {xls|xlsx|csv} <input> [-s <selectors>] [--output-dir <dir>]`  
  Generate dbt models for all or selected nodes.
- `turbovault list -f {xls|xlsx|csv} <input> [-s <selectors>]`  
  List resolved nodes for a selector (dry run).

#### Arguments:
- `-f, --format`: Input format. Must be one of: `xls`, `xlsx`, `csv`
- `input`: Path to Excel file (`.xls`/`.xlsx`) or folder containing CSV files (for `csv`)
- `-s, --select`: (Optional) Node selectors (space-separated).  
   Examples: `hub1`, `+sat1`, `hub2+`, `@masat3`
- `--output-dir`: (Optional) Output directory for generated files

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
pytest tests/
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
See [PyPI Releases](https://pypi.org/project/turbovault4dbt/)

---

## License
See [LICENSE](LICENSE)

---

## Need Help?
- [Open an issue](https://github.com/InfoMatePL/turbovault4dbt_cli/issues)
- [Wiki](https://github.com/ScalefreeCOM/turbovault4dbt/wiki)