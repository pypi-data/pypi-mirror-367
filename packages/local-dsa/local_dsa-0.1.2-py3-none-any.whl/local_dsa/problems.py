import sqlite3
from .database import DB_PATH

def insert_problem(problem_name, problem_statement):
    """Insert a new problem into the problems table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO problems (problem_name, problem_statement)
        VALUES (?, ?)
    """, (problem_name, problem_statement))
    problem_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Inserted problem '{problem_name}' with ID {problem_id}")
    return problem_id

def insert_test_case(problem_id, test_case, correct_ans):
    """Insert a new test case for a given problem."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO test_cases (problemId, test_case, correct_ans)
        VALUES (?, ?, ?)
    """, (problem_id, test_case, correct_ans))
    conn.commit()
    conn.close()
    print(f"Inserted test case '{test_case}' with expected answer '{correct_ans}' for problemId={problem_id}")
