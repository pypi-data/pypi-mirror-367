import sqlite3
import inspect
import re

from .check_solutions import run_test_cases
from .code_storage import store_function_to_db

DB_PATH = "code_storage.db"


def get_similar_problems(q):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, problem_name FROM problems 
        WHERE problem_name LIKE ? 
        LIMIT 5
    """, (f"%{q}%",))
    results = cursor.fetchall()
    conn.close()
    return results


def get_problem_details(problem_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT problem_name, problem_statement FROM problems WHERE id = ?
    """, (problem_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def add_comments_after_question_object(file_path, matches, problem_detail):
    with open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        # Detect question.name assignment
        if re.match(r"^\s*question\.name\s*=", line):
            # Remove old comments
            while i + 1 < len(lines) and lines[i + 1].strip().startswith("## Problem found here:"):
                del lines[i + 1]
            for match in matches:
                problem_id, problem_name = match
                lines.insert(i + 1, f"## Problem found here: [ID: {problem_id}] {problem_name}\n")
                i += 1

        # Detect question.id assignment
        if re.match(r"^\s*question\.id\s*=", line):
            while i + 1 < len(lines) and lines[i + 1].strip().startswith("##"):
                del lines[i + 1]
            if problem_detail:
                problem_name, problem_statement = problem_detail
                lines.insert(i + 1, f"## Attempting problem: {problem_name}\n")
                for stmt_line in problem_statement.splitlines():
                    lines.insert(i + 2, f"## {stmt_line}\n")
    with open(file_path, "w") as f:
        f.writelines(lines)


def solve_problem(question, solver_class):
    caller_file = inspect.stack()[1].filename

    if not question.name:
        print("No question specified.")
        return

    matches = get_similar_problems(question.name)
    if matches:
        problem_detail = get_problem_details(question.id) if question.id else None
        add_comments_after_question_object(caller_file, matches, problem_detail)

    solver = solver_class()
    run_test_cases(question.id, lambda *args: solver.solve(*args))
    store_function_to_db(solver_class, question.id)

def test_problem(question, solver_class):
    caller_file = inspect.stack()[1].filename

    if not question.name:
        print("No question specified.")
        return

    matches = get_similar_problems(question.name)
    if matches:
        problem_detail = get_problem_details(question.id) if question.id else None
        add_comments_after_question_object(caller_file, matches, problem_detail)

    solver = solver_class()
    run_test_cases(question.id, lambda *args: solver.solve(*args))
