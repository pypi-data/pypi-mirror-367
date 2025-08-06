import sqlite3

DB_PATH = "code_storage.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table: Topic
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT
        )
    """)

    # Table: Problems
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_name TEXT,
            problem_statement TEXT,
            test_cases TEXT,
            constraints TEXT
        )
    """)

    # Table: ProblemTopic (Many-to-many between Problems and Topic)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problem_topic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problemId INTEGER,
            topicId INTEGER,
            FOREIGN KEY (problemId) REFERENCES problems(id),
            FOREIGN KEY (topicId) REFERENCES topic(id)
        )
    """)

    # Table: TestCases
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problemId INTEGER,
            test_case TEXT,
            correct_ans TEXT,
            FOREIGN KEY (problemId) REFERENCES problems(id)
        )
    """)

    # Table: Submissions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problemId INTEGER,
            fileName TEXT,
            code TEXT,
            date_time TEXT,
            FOREIGN KEY (problemId) REFERENCES problems(id)
        )
    """)

    conn.commit()
    conn.close()

init_db()
