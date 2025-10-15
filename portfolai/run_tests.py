#!/usr/bin/env python
"""
Test runner script for PortfolAI
Usage: python run_tests.py [options]
"""
import sys
import subprocess
import argparse


def run_tests(args):
    """Run tests with specified options"""
    cmd = ["pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    if args.parallel:
        cmd.extend(["-n", "auto"])
    
    if args.html:
        cmd.extend(["--html=test_report.html", "--self-contained-html"])
    
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    if args.file:
        cmd.append(args.file)
    else:
        cmd.append("test_api.py")
    
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode


def main():
    parser = argparse.ArgumentParser(description="Run PortfolAI tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("-p", "--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("-m", "--markers", help="Run tests with specific markers")
    parser.add_argument("-f", "--file", help="Run specific test file")
    
    args = parser.parse_args()
    
    exit_code = run_tests(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
