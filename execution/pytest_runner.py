import os
import sys
import tempfile
import subprocess
import re
import json
import time
from schemas.state import TestExecutionResult, TestCaseDetail

def run_tests_in_sandbox(code: str, test_code: str, timeout: float = 5.0) -> TestExecutionResult:
    """
    Executes generated code against unit test code in an isolated temporary environment.
    Safely evaluates individual assertions / test functions and captures stdout, stderr,
    and individual test case pass/fail results.
    """
    if not code or not code.strip():
        return TestExecutionResult(
            passed=False,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            test_details=[],
            stdout="",
            stderr="No code provided for execution.",
            error_type="EmptyCodeError"
        )
        
    if not test_code or not test_code.strip():
        try:
            compile(code, "<string>", "exec")
            return TestExecutionResult(
                passed=True,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                test_details=[],
                stdout="Syntax check passed (No unit tests specified).",
                stderr="",
                error_type=None
            )
        except SyntaxError as e:
            return TestExecutionResult(
                passed=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                test_details=[],
                stdout="",
                stderr=f"SyntaxError: {e}",
                error_type="SyntaxError"
            )

    with tempfile.TemporaryDirectory() as tmpdir:
        solution_path = os.path.join(tmpdir, "solution.py")
        harness_path = os.path.join(tmpdir, "test_harness.py")
        results_path = os.path.join(tmpdir, "results.json")
        spec_path = os.path.join(tmpdir, "test_spec.txt")
        
        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(test_code)

        # Build an isolated execution harness script
        harness_code = """
import sys
import os
import json
import traceback

results_path = "results.json"
spec_path = "test_spec.txt"

with open(spec_path, "r", encoding="utf-8") as f:
    raw_test_code = f.read()

results = []

try:
    from solution import *
except Exception as e:
    tb = traceback.format_exc()
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({"import_error": str(e), "traceback": tb, "tests": []}, f)
    sys.exit(1)

# Check if test code uses def test_
if "def test_" in raw_test_code:
    import pytest
    with open("test_spec.py", "w", encoding="utf-8") as f:
        f.write("from solution import *\\n\\n" + raw_test_code)
        
    code_res = pytest.main(["test_spec.py", "-q"])
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({"pytest_mode": True, "passed": (code_res == 0), "tests": []}, f)
else:
    lines = [l for l in raw_test_code.splitlines() if l.strip() and not l.strip().startswith("#")]
    for idx, line in enumerate(lines, 1):
        test_info = {"name": f"Test #{idx}", "assertion": line, "passed": False, "error": None}
        try:
            exec(line, globals())
            test_info["passed"] = True
        except AssertionError:
            test_info["error"] = "AssertionError: Condition evaluated to False"
        except Exception as ex:
            test_info["error"] = f"{type(ex).__name__}: {ex}"
        results.append(test_info)
        
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({"pytest_mode": False, "tests": results}, f)
"""
        with open(harness_path, "w", encoding="utf-8") as f:
            f.write(harness_code)
            
        try:
            result = subprocess.run(
                [sys.executable, harness_path],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            stdout = result.stdout
            stderr = result.stderr
            
            # Read results.json
            if os.path.exists(results_path):
                with open(results_path, "r", encoding="utf-8") as rf:
                    res_data = json.load(rf)
                    
                if "import_error" in res_data:
                    return TestExecutionResult(
                        passed=False,
                        total_tests=1,
                        passed_tests=0,
                        failed_tests=1,
                        test_details=[TestCaseDetail(name="Import Check", assertion="from solution import *", passed=False, error=res_data["import_error"])],
                        stdout=stdout.strip(),
                        stderr=res_data["traceback"].strip(),
                        error_type="ImportError"
                    )
                    
                if res_data.get("pytest_mode"):
                    pytest_passed = res_data["passed"]
                    test_count = max(1, len(re.findall(r"def test_", test_code)))
                    return TestExecutionResult(
                        passed=pytest_passed,
                        total_tests=test_count,
                        passed_tests=test_count if pytest_passed else 0,
                        failed_tests=0 if pytest_passed else test_count,
                        test_details=[TestCaseDetail(name=f"pytest_suite_{i+1}", assertion=f"test_case_{i+1}", passed=pytest_passed) for i in range(test_count)],
                        stdout=stdout.strip(),
                        stderr=stderr.strip(),
                        error_type=None if pytest_passed else "AssertionError"
                    )
                    
                test_details = []
                passed_cnt = 0
                for t in res_data.get("tests", []):
                    if t["passed"]:
                        passed_cnt += 1
                    test_details.append(TestCaseDetail(
                        name=t["name"],
                        assertion=t["assertion"],
                        passed=t["passed"],
                        error=t.get("error")
                    ))
                    
                total_cnt = len(test_details)
                all_passed = (passed_cnt == total_cnt and total_cnt > 0)
                
                error_type = None
                if not all_passed:
                    first_err = next((t.error for t in test_details if not t.passed and t.error), "AssertionError")
                    error_type = first_err.split(":")[0]
                    
                return TestExecutionResult(
                    passed=all_passed,
                    total_tests=total_cnt,
                    passed_tests=passed_cnt,
                    failed_tests=total_cnt - passed_cnt,
                    test_details=test_details,
                    stdout=stdout.strip(),
                    stderr=stderr.strip(),
                    error_type=error_type
                )
                
            # If results.json wasn't written
            passed = (result.returncode == 0)
            combined_err = f"{stdout}\n{stderr}"
            error_type = "SyntaxError" if "SyntaxError" in combined_err else "RuntimeError"
            return TestExecutionResult(
                passed=passed,
                total_tests=1,
                passed_tests=1 if passed else 0,
                failed_tests=0 if passed else 1,
                test_details=[],
                stdout=stdout.strip(),
                stderr=stderr.strip(),
                error_type=None if passed else error_type
            )
            
        except subprocess.TimeoutExpired:
            return TestExecutionResult(
                passed=False,
                total_tests=1,
                passed_tests=0,
                failed_tests=1,
                test_details=[],
                stdout="",
                stderr=f"Execution timed out after {timeout} seconds (potential infinite loop).",
                error_type="TimeoutError"
            )
        except Exception as e:
            return TestExecutionResult(
                passed=False,
                total_tests=1,
                passed_tests=0,
                failed_tests=1,
                test_details=[],
                stdout="",
                stderr=f"Execution failed to launch: {e}",
                error_type="ExecutionEngineError"
            )


def run_custom_input_in_sandbox(code: str, custom_input: str, timeout: float = 5.0) -> dict:
    """
    Executes a custom function call or input expression against the generated code in a sandbox.
    Returns return_value, stdout, stderr, execution_time_ms, and status.
    """
    if not code or not code.strip():
        return {
            "success": False,
            "return_value": None,
            "stdout": "",
            "stderr": "No code provided to execute.",
            "execution_time_ms": 0.0,
            "error": "EmptyCodeError"
        }

    input_str = custom_input.strip()
    if not input_str:
        return {
            "success": False,
            "return_value": None,
            "stdout": "",
            "stderr": "No custom input provided.",
            "execution_time_ms": 0.0,
            "error": "EmptyInputError"
        }

    # Find the primary function name defined in code if the user passed raw arguments like `"racecar"` or `5`
    func_names = re.findall(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", code)
    primary_func = func_names[0] if func_names else None

    # Check if input_str already calls a function
    has_call = bool(re.search(r"[a-zA-Z_][a-zA-Z0-9_]*\s*\(", input_str))
    
    # If the user passed raw input like '"racecar"' or '5' and a function exists, wrap it in primary_func(...)
    formatted_expr = input_str
    if not has_call and primary_func and not "=" in input_str and not "\n" in input_str:
        formatted_expr = f"{primary_func}({input_str})"

    with tempfile.TemporaryDirectory() as tmpdir:
        solution_path = os.path.join(tmpdir, "solution.py")
        runner_path = os.path.join(tmpdir, "runner.py")
        out_json_path = os.path.join(tmpdir, "output.json")
        
        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(code)

        with open(os.path.join(tmpdir, "input_expr.txt"), "w", encoding="utf-8") as f:
            f.write(formatted_expr)

        runner_code = """
import sys
import io
import json
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr

out_file = "output.json"
with open("input_expr.txt", "r", encoding="utf-8") as f:
    expr = f.read().strip()

captured_stdout = io.StringIO()
captured_stderr = io.StringIO()
return_val = None
success = False
err_msg = None

start_time = time.perf_counter()

try:
    with redirect_stdout(captured_stdout), redirect_stderr(captured_stderr):
        from solution import *
        
        # Check if expr is a single expression or multiple lines/statements
        try:
            compiled = compile(expr, "<custom_input>", "eval")
            return_val = eval(compiled, globals())
            success = True
        except SyntaxError:
            # Execute as statements
            compiled = compile(expr, "<custom_input>", "exec")
            exec(compiled, globals())
            success = True
            
except Exception as e:
    err_msg = f"{type(e).__name__}: {e}"
    tb = traceback.format_exc()
    captured_stderr.write(tb)
    success = False

elapsed_ms = (time.perf_counter() - start_time) * 1000.0

try:
    # Serialize return_val cleanly
    formatted_val = repr(return_val) if return_val is not None else None
except Exception:
    formatted_val = str(return_val)

res = {
    "success": success,
    "return_value": formatted_val,
    "stdout": captured_stdout.getvalue().strip(),
    "stderr": captured_stderr.getvalue().strip(),
    "execution_time_ms": round(elapsed_ms, 2),
    "error": err_msg,
    "expression_evaluated": expr
}

with open(out_file, "w", encoding="utf-8") as f:
    json.dump(res, f)
"""
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write(runner_code)

        try:
            sub = subprocess.run(
                [sys.executable, runner_path],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if os.path.exists(out_json_path):
                with open(out_json_path, "r", encoding="utf-8") as rf:
                    return json.load(rf)

            return {
                "success": False,
                "return_value": None,
                "stdout": sub.stdout.strip(),
                "stderr": sub.stderr.strip() or "Runner failed to return output.",
                "execution_time_ms": 0.0,
                "error": "ExecutionError"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "return_value": None,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds.",
                "execution_time_ms": timeout * 1000.0,
                "error": "TimeoutError"
            }
        except Exception as ex:
            return {
                "success": False,
                "return_value": None,
                "stdout": "",
                "stderr": f"Sandbox execution error: {ex}",
                "execution_time_ms": 0.0,
                "error": type(ex).__name__
            }
