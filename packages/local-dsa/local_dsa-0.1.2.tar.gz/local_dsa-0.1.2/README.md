# Local DSA

**local_dsa** is a Python package designed to streamline coding problem-solving.  
It automatically fetches related problem suggestions from a local database,  
inserts automated comments into your code, and allows you to run solution tests  
easily just from a single .py file

---

## Features
- **Global `question` object**  
  Easily set and access:
  ```python
  from local_dsa import question

  question.name = "Sum of Two Numbers"
  question.id = 1
  ```
- **Automatic problem suggestions**  
  Finds similar problems and inserts comments directly after your `question.name` line.
- **Problem statement injection**  
  Adds the problem statement after `question.id` line.
- **Solution testing & storage**  
  - `test_problem()` → runs test cases without storing code  
  - `solve_problem()` → runs test cases and stores your solution in the database.

---

## Installation
Install using pip:
```bash
pip install local-dsa
```

---

## Quick Start

### Example usage:
```python
from local_dsa import question, test_problem

# Set question details
question.name = "Sum of Two Numbers"
question.id = 1

class SumTwoNumbers:
    def solve(self, a, b):
        return a + b

# Test the solution
test_problem(question, SumTwoNumbers)
```

**Expected auto-comments in your file after saving & running:**
```python
question.name = "Sum of Two Numbers"
## Problem found here: [ID: 1] Sum of Two Numbers

question.id = 1
## Attempting problem: Sum of Two Numbers
## Given two integers, return their sum.
```

---

## Command Overview
- **`solve_problem(question, solver_class)`**  
  Runs test cases and stores the function code.
- **`test_problem(question, solver_class)`**  
  Runs test cases without storing.

---

## Project Structure
```
local_dsa/
├── __init__.py
├── question.py
├── main.py
├── check_solutions.py
├── code_storage.py
```

---

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
