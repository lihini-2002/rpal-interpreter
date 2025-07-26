"""
Test framework for comparing the output of our RPAL interpreter with the original RPAL interpreter.
Runs test programs through both interpreters and verifies that the outputs match.
"""

import os
import subprocess
import difflib
from pathlib import Path

def run_rpal_exe(file_path):
    """
    Run a test file using the original RPAL interpreter (rpal.exe).
    
    Args:
        file_path: Path to the RPAL test file
        
    Returns:
        str: Output from the original interpreter or error message
    """
    try:
        result = subprocess.run(['original-interpreter/rpal.exe', str(file_path)], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error running rpal.exe: {e.stderr}"

def run_myrpal(file_path):
    """
    Run a test file using our RPAL interpreter (myrpal.py).
    
    Args:
        file_path: Path to the RPAL test file
        
    Returns:
        str: Output from our interpreter or error message
    """
    try:
        result = subprocess.run(['python', 'myrpal.py', str(file_path)], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error running myrpal.py: {e.stderr}"

def compare_outputs(original, mine, filename):
    """
    Compare outputs from both interpreters and generate a diff if they don't match.
    
    Args:
        original: Output from the original interpreter
        mine: Output from our interpreter
        filename: Name of the test file (for reporting)
        
    Returns:
        tuple: (bool indicating if outputs match, diff string if they don't)
    """
    if original == mine:
        return True, ""
    
    # Generate a unified diff for better readability
    diff = list(difflib.unified_diff(
        original.splitlines(),
        mine.splitlines(),
        fromfile='rpal.exe output',
        tofile='myrpal.py output',
        lineterm=''
    ))
    return False, '\n'.join(diff)

def run_tests():
    """
    Run all test files in the test-programs directory and report results.
    Compares outputs from both interpreters and provides a detailed test summary.
    """
    # Find all RPAL test files
    test_dir = Path('test-programs')
    test_files = sorted(test_dir.glob('*.rpal'))
    
    total_tests = len(test_files)
    passed_tests = 0
    failed_tests = []
    
    print(f"\nRunning {total_tests} test files...\n")
    print("=" * 80)
    
    # Run each test file
    for test_file in test_files:
        print(f"\nTesting: {test_file.name}")
        print("-" * 40)
        
        # Get outputs from both interpreters
        rpal_output = run_rpal_exe(test_file)
        myrpal_output = run_myrpal(test_file)
        
        # Compare and report results
        passed, diff = compare_outputs(rpal_output, myrpal_output, test_file.name)
        
        if passed:
            print("✅ PASSED")
            passed_tests += 1
        else:
            print("❌ FAILED")
            print("\nDifferences found:")
            print(diff)
            failed_tests.append(test_file.name)
        
        print("-" * 40)
    
    # Print test summary
    print("\n" + "=" * 80)
    print(f"\nTest Summary:")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    
    if failed_tests:
        print("\nFailed tests:")
        for test in failed_tests:
            print(f"- {test}")

if __name__ == "__main__":
    run_tests() 