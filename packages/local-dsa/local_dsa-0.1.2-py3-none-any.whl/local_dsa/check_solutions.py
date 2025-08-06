import sqlite3
from .database import DB_PATH

def run_test_cases(problem_id, solution_func):
    """Run all test cases for a problem using a given solution function.
    
    Args:
        problem_id (int): ID of the problem
        solution_func (callable): Function to test. It should take arguments based on test cases.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get test cases for this problem (correct column name is problemId)
    cursor.execute("""
        SELECT test_case, correct_ans FROM test_cases
        WHERE problemId=?
    """, (problem_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No test cases found for problem ID {problem_id}")
        return

    all_passed = True
    print(f"\nRunning test cases for problem id={problem_id}")
    for idx, (test_case, correct_ans) in enumerate(rows, 1):
        # Convert input string to list of integers (basic format)
        # Adjust parsing logic depending on your test case input type
        inputs = list(map(int, test_case.strip().split()))
        
        try:
            result = solution_func(*inputs)  # unpack arguments
        except Exception as e:
            print(f"Test case {idx} failed with error: {e}")
            all_passed = False
            continue

        if str(result) == str(correct_ans):
            print(f"Test case {idx}: PASS")
        else:
            print(f"Test case {idx}: FAIL (Expected {correct_ans}, Got {result})")
            all_passed = False

    print("\nAll Test Cases Passed!" if all_passed else "\nSome Test Cases Failed!")
