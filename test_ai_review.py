#!/usr/bin/env python3
"""
Test file to trigger AI code review
This file contains some code that the AI can review
"""

def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def process_user_data(user_data):
    """Process user data with some potential issues for AI to catch"""
    result = {}
    
    # Potential issue: no input validation
    for key, value in user_data.items():
        result[key] = value * 2
    
    # Another potential issue: hardcoded values
    if len(result) > 10:
        return "Too many items"
    
    return result

def main():
    """Main function"""
    print("Testing AI code review workflow")
    
    # Test the functions
    fib_result = calculate_fibonacci(5)
    print(f"Fibonacci(5) = {fib_result}")
    
    # Test with sample data
    sample_data = {"a": 1, "b": 2, "c": 3}
    processed = process_user_data(sample_data)
    print(f"Processed data: {processed}")

if __name__ == "__main__":
    main()
