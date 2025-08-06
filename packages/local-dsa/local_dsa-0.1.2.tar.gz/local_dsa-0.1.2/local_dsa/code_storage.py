import sqlite3
import inspect
from datetime import datetime
from .database import DB_PATH

def store_function_to_db(func, problem_id):
    """Stores only the given function's code into submissions table for a given problem"""
    func_code = inspect.getsource(func)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO submissions (problemId, fileName, code, date_time)
        VALUES (?, ?, ?, ?)
    """, (problem_id, func.__name__, func_code, timestamp))
    conn.commit()
    conn.close()
    print(f"Inserted function '{func.__name__}' for problemId={problem_id} into {DB_PATH} at {timestamp}")
