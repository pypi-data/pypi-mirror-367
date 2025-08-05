import subprocess
import filecmp
import os
import pytest

CASES_DIR = os.path.dirname(__file__)

# Map test case to selector (None means no selector)
CASE_SELECTORS = {
    'case_01': None,
    'case_02': '+sat1 hub2+ @masat3',
    'case_03': 'hub1',
    'case_04': '+pit2',
    'case_05': '@sat1',
}

NEGATIVE_CASES = [
    'fail_no_command',
]

def run_cli(input_xlsx, output_dir, selector=None):
    print(f"\n[run_cli] INPUT: {input_xlsx}")
    print(f"[run_cli] OUTPUT DIR: {output_dir}")
    print(f"[run_cli] SELECTOR: {selector}")
    cmd = [
        "turbovault", "run",
        "--file", input_xlsx,
        "--output-dir", output_dir
    ]
    if selector:
        cmd += ["-s"] + selector.split()
    print(f"[run_cli] CMD: {' '.join(cmd)}")
    env = os.environ.copy()
    result = subprocess.run(cmd, cwd=os.path.dirname(input_xlsx), env=env, capture_output=True, text=True)
    print(f"[run_cli] CLI STDOUT:\n{result.stdout}")
    print(f"[run_cli] CLI STDERR:\n{result.stderr}")
    print(f"[run_cli] FILES GENERATED: {os.listdir(output_dir)}")
    assert result.returncode == 0, f"CLI failed: {result.stderr}\n{result.stdout}"

def compare_dirs(dir1, dir2):
    print(f"\n[compare_dirs] Comparing:\n  GENERATED: {dir1}\n  EXPECTED:  {dir2}")
    print(f"[compare_dirs] GENERATED FILES: {sorted(os.listdir(dir1))}")
    print(f"[compare_dirs] EXPECTED  FILES: {sorted(os.listdir(dir2))}")
    comp = filecmp.dircmp(dir1, dir2)
    if comp.left_only or comp.right_only:
        print(f"[compare_dirs] ONLY IN GENERATED: {comp.left_only}")
        print(f"[compare_dirs] ONLY IN EXPECTED: {comp.right_only}")
    for fname in comp.common_files:
        with open(os.path.join(dir1, fname)) as f1, open(os.path.join(dir2, fname)) as f2:
            if f1.read() != f2.read():
                print(f"[compare_dirs] CONTENT DIFF: {fname}")
    assert not comp.left_only and not comp.right_only, f"Files differ: {comp.left_only}, {comp.right_only}"
    for fname in comp.common_files:
        with open(os.path.join(dir1, fname)) as f1, open(os.path.join(dir2, fname)) as f2:
            assert f1.read() == f2.read(), f"File {fname} differs"


@pytest.mark.parametrize("case_dir", [
    d for d in os.listdir(CASES_DIR) if os.path.isdir(os.path.join(CASES_DIR, d)) and d.startswith("case_")
])
def test_regression(case_dir, tmp_path):
    if case_dir in NEGATIVE_CASES:
        # Negative test: expect CLI to fail
        result = subprocess.run(["turbovault"], capture_output=True, text=True)
        assert result.returncode != 0, "Expected turbovault to fail without subcommand"
        return
    case_path = os.path.join(CASES_DIR, case_dir)
    input_xlsx = os.path.join(case_path, "input.xlsx")
    expected_output = os.path.join(case_path, "expected_output")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    selector = CASE_SELECTORS.get(case_dir)
    run_cli(input_xlsx, str(output_dir), selector)
    compare_dirs(str(output_dir), expected_output) 