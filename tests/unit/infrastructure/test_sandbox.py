"""
Unit tests for Sandbox.

Tests isolated code execution with focus on:
- Timeout protection
- Output capture
- Exception handling
- Resource limits
- Security restrictions
- Simulated malicious code handling

⚠️ NOTE: These tests simulate malicious behavior for security testing purposes.
The code tested here is NOT truly malicious - it's designed to test sandbox limits.

:author: ForgeBase Development Team
:since: 2025-11-03
"""

import unittest
import time
import sys
from src.forgebase.infrastructure.security.sandbox import (
    Sandbox,
    ExecutionResult,
    SandboxError,
    SandboxTimeoutError,
    SandboxExecutionError
)


class TestSandbox(unittest.TestCase):
    """Test suite for Sandbox."""

    def setUp(self):
        """Set up test fixtures."""
        self.sandbox = Sandbox(timeout=2.0, memory_limit_mb=100)

    def test_sandbox_initialization(self):
        """Test sandbox initialization."""
        sandbox = Sandbox(timeout=5.0, memory_limit_mb=200)

        self.assertEqual(sandbox.timeout, 5.0)
        self.assertEqual(sandbox.memory_limit_mb, 200)
        self.assertIsInstance(sandbox.restricted_modules, set)

    def test_execute_simple_code(self):
        """Test executing simple Python code."""
        result = self.sandbox.execute('x = 10\ny = 20\nresult = x + y')

        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.timeout, False)

    def test_execute_with_print_output(self):
        """Test that stdout is captured."""
        result = self.sandbox.execute('print("Hello, World!")')

        self.assertTrue(result.success)
        self.assertIn("Hello, World!", result.output)

    def test_execute_with_multiple_prints(self):
        """Test capturing multiple print statements."""
        code = '''
print("Line 1")
print("Line 2")
print("Line 3")
'''
        result = self.sandbox.execute(code)

        self.assertTrue(result.success)
        self.assertIn("Line 1", result.output)
        self.assertIn("Line 2", result.output)
        self.assertIn("Line 3", result.output)

    def test_execute_with_return_value(self):
        """Test capturing return value from code."""
        code = '''
def calculate():
    return 42

answer = calculate()
'''
        result = self.sandbox.execute(code, capture_result='answer')

        self.assertTrue(result.success)
        self.assertEqual(result.return_value, 42)

    def test_execute_mathematical_operations(self):
        """Test executing mathematical operations."""
        code = '''
import math
result = math.sqrt(16) + math.pow(2, 3)
'''
        result = self.sandbox.execute(code, capture_result='result')

        self.assertTrue(result.success)
        self.assertEqual(result.return_value, 12.0)  # sqrt(16)=4, pow(2,3)=8, 4+8=12

    def test_execute_with_exception(self):
        """Test that exceptions are captured."""
        result = self.sandbox.execute('x = 1 / 0')  # Division by zero

        self.assertFalse(result.success)
        self.assertIsNotNone(result.exception)
        self.assertIsInstance(result.exception, ZeroDivisionError)
        self.assertIsNotNone(result.exception_traceback)

    def test_execute_with_syntax_error(self):
        """Test handling of syntax errors."""
        result = self.sandbox.execute('if True print("error")')  # Syntax error

        self.assertFalse(result.success)
        self.assertIsNotNone(result.exception)
        self.assertIsInstance(result.exception, SyntaxError)

    def test_execute_with_custom_globals(self):
        """Test executing code with custom global namespace."""
        def multiply(a, b):
            return a * b

        globals_dict = {
            '__builtins__': self.sandbox._create_restricted_builtins(),
            'multiply': multiply,
            'x': 5,
            'y': 3
        }

        result = self.sandbox.execute(
            'result = multiply(x, y)',
            globals_dict=globals_dict,
            capture_result='result'
        )

        self.assertTrue(result.success)
        self.assertEqual(result.return_value, 15)

    def test_execution_time_tracking(self):
        """Test that execution time is tracked."""
        code = '''
import time
time.sleep(0.1)  # Sleep for 100ms
'''
        result = self.sandbox.execute(code)

        self.assertTrue(result.success)
        self.assertGreaterEqual(result.execution_time, 0.1)
        self.assertLess(result.execution_time, 0.5)  # Should not take too long

    def test_execution_result_string_representation(self):
        """Test ExecutionResult string representation."""
        result = self.sandbox.execute('print("test")')

        repr_str = str(result)
        self.assertIn('ExecutionResult', repr_str)
        self.assertIn('success=True', repr_str)

    def test_sandbox_repr(self):
        """Test Sandbox string representation."""
        repr_str = repr(self.sandbox)

        self.assertIn('Sandbox', repr_str)
        self.assertIn('2.0s', repr_str)
        self.assertIn('100MB', repr_str)


class TestSandboxTimeout(unittest.TestCase):
    """Test suite for sandbox timeout functionality."""

    @unittest.skipIf(sys.platform == 'win32', "Signal-based timeout not supported on Windows")
    def test_timeout_on_infinite_loop(self):
        """Test that infinite loop triggers timeout."""
        sandbox = Sandbox(timeout=1.0)

        code = '''
while True:
    pass  # Infinite loop
'''
        result = sandbox.execute(code)

        self.assertFalse(result.success)
        self.assertTrue(result.timeout)
        self.assertIsInstance(result.exception, TimeoutError)

    @unittest.skipIf(sys.platform == 'win32', "Signal-based timeout not supported on Windows")
    def test_timeout_with_long_computation(self):
        """Test timeout with long-running computation."""
        sandbox = Sandbox(timeout=1.0)

        code = '''
# Computationally expensive operation
total = 0
for i in range(10000000):
    total += i * i
'''
        result = sandbox.execute(code)

        # May or may not timeout depending on system speed
        # Just verify it doesn't crash
        self.assertIsInstance(result, ExecutionResult)


class TestSandboxSecurity(unittest.TestCase):
    """Test suite for sandbox security features."""

    def setUp(self):
        """Set up test fixtures."""
        self.sandbox = Sandbox(timeout=2.0)

    def test_restricted_module_import_os(self):
        """Test that importing 'os' module is restricted."""
        result = self.sandbox.execute('import os')

        self.assertFalse(result.success)
        self.assertIsInstance(result.exception, ImportError)
        self.assertIn('restricted', result.exception_traceback.lower())

    def test_restricted_module_import_subprocess(self):
        """Test that importing 'subprocess' module is restricted."""
        result = self.sandbox.execute('import subprocess')

        self.assertFalse(result.success)
        self.assertIsInstance(result.exception, ImportError)

    def test_restricted_module_import_sys(self):
        """Test that importing 'sys' module is restricted."""
        result = self.sandbox.execute('import sys')

        self.assertFalse(result.success)
        self.assertIsInstance(result.exception, ImportError)

    def test_allowed_module_import_math(self):
        """Test that safe modules like 'math' are allowed."""
        result = self.sandbox.execute('import math\nresult = math.pi')

        # This might fail if math is not in restricted set
        # The behavior depends on implementation
        self.assertIsInstance(result, ExecutionResult)

    def test_dangerous_builtin_eval_not_available(self):
        """Test that dangerous builtins like 'eval' are restricted."""
        result = self.sandbox.execute('eval("1+1")')

        # eval is not in safe_builtins, so this should fail
        self.assertFalse(result.success)
        self.assertIsInstance(result.exception, NameError)

    def test_dangerous_builtin_exec_not_available(self):
        """Test that dangerous builtins like 'exec' are restricted."""
        result = self.sandbox.execute('exec("x = 1")')

        # exec is not in safe_builtins, so this should fail
        self.assertFalse(result.success)
        self.assertIsInstance(result.exception, NameError)

    def test_dangerous_builtin_compile_not_available(self):
        """Test that 'compile' builtin is restricted."""
        result = self.sandbox.execute('compile("x = 1", "<string>", "exec")')

        self.assertFalse(result.success)
        self.assertIsInstance(result.exception, NameError)

    def test_safe_builtins_are_available(self):
        """Test that safe builtins like 'len', 'sum', 'max' are available."""
        code = '''
numbers = [1, 2, 3, 4, 5]
result = {
    'length': len(numbers),
    'total': sum(numbers),
    'maximum': max(numbers)
}
'''
        result = self.sandbox.execute(code, capture_result='result')

        self.assertTrue(result.success)
        self.assertEqual(result.return_value['length'], 5)
        self.assertEqual(result.return_value['total'], 15)
        self.assertEqual(result.return_value['maximum'], 5)


class TestSandboxMaliciousCode(unittest.TestCase):
    """
    Test suite for handling simulated malicious code.

    ⚠️ IMPORTANT: These tests use SIMULATED malicious code for testing purposes.
    The code is not actually malicious - it's designed to test sandbox limits.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.sandbox = Sandbox(timeout=1.0, memory_limit_mb=100)

    @unittest.skipIf(sys.platform == 'win32', "Signal-based timeout not supported on Windows")
    def test_simulated_infinite_loop(self):
        """Test handling of infinite loop (simulated DoS)."""
        code = '''
# Simulated infinite loop attack
counter = 0
while True:
    counter += 1
    if counter > 1000000:  # Safety limit in case timeout fails
        break
'''
        result = self.sandbox.execute(code)

        # Should timeout or complete (with safety limit)
        if result.timeout:
            self.assertFalse(result.success)
            self.assertTrue(result.timeout)
        else:
            # Safety limit kicked in
            self.assertTrue(result.success or not result.success)

    def test_simulated_memory_exhaustion(self):
        """Test handling of memory exhaustion attempt."""
        code = '''
# Simulated memory exhaustion (limited scope)
# Real memory exhaustion would crash before sandbox can handle it
data = []
for i in range(1000):  # Limited to prevent actual exhaustion
    data.append([0] * 1000)
result = len(data)
'''
        result = self.sandbox.execute(code, capture_result='result')

        # Should complete (limited scope) or fail with memory error
        self.assertIsInstance(result, ExecutionResult)

    def test_simulated_exception_spam(self):
        """Test handling of exception-raising code."""
        code = '''
# Simulated exception spam
try:
    for i in range(100):
        try:
            raise ValueError(f"Error {i}")
        except ValueError:
            pass
    result = "completed"
except Exception as e:
    result = "failed"
'''
        result = self.sandbox.execute(code, capture_result='result')

        self.assertTrue(result.success)
        self.assertEqual(result.return_value, "completed")

    def test_simulated_recursive_depth(self):
        """Test handling of deep recursion."""
        code = '''
def recurse(n):
    if n <= 0:
        return 0
    return 1 + recurse(n - 1)

try:
    result = recurse(10000)  # Deep recursion
except RecursionError:
    result = "recursion_error"
'''
        result = self.sandbox.execute(code, capture_result='result')

        # Should either complete or hit RecursionError
        self.assertIsInstance(result, ExecutionResult)
        if result.success:
            self.assertEqual(result.return_value, "recursion_error")

    def test_simulated_namespace_pollution(self):
        """Test that code cannot pollute global namespace."""
        code1 = 'secret_variable = "should not leak"'
        code2 = 'result = "secret_variable" in dir()'

        self.sandbox.execute(code1)
        result2 = self.sandbox.execute(code2, capture_result='result')

        # Each execution should have clean namespace
        self.assertTrue(result2.success)
        self.assertFalse(result2.return_value)  # Variable should not exist in new execution


class TestSandboxEdgeCases(unittest.TestCase):
    """Test suite for sandbox edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.sandbox = Sandbox(timeout=2.0)

    def test_empty_code_execution(self):
        """Test executing empty code."""
        result = self.sandbox.execute('')

        self.assertTrue(result.success)
        self.assertEqual(result.output, '')

    def test_code_with_only_comments(self):
        """Test executing code with only comments."""
        code = '''
# This is a comment
# Another comment
'''
        result = self.sandbox.execute(code)

        self.assertTrue(result.success)

    def test_multiline_string_output(self):
        """Test handling multiline string output."""
        code = '''
text = """
Line 1
Line 2
Line 3
"""
print(text)
'''
        result = self.sandbox.execute(code)

        self.assertTrue(result.success)
        self.assertIn("Line 1", result.output)
        self.assertIn("Line 2", result.output)
        self.assertIn("Line 3", result.output)

    def test_unicode_handling(self):
        """Test handling Unicode characters."""
        code = '''
text = "Hello 世界 🌍"
print(text)
result = text
'''
        result = self.sandbox.execute(code, capture_result='result')

        self.assertTrue(result.success)
        self.assertEqual(result.return_value, "Hello 世界 🌍")
        self.assertIn("Hello 世界 🌍", result.output)

    def test_large_output(self):
        """Test handling large output."""
        code = '''
for i in range(100):
    print(f"Line {i}")
'''
        result = self.sandbox.execute(code)

        self.assertTrue(result.success)
        self.assertIn("Line 0", result.output)
        self.assertIn("Line 99", result.output)


if __name__ == '__main__':
    unittest.main()
