# Test Task Traektory

## Description
This project is a Python-based application designed to perform specific tasks. The codebase is organized into `src` for the main application logic and `tests` for unit tests.

## Requirements
- Python 3.6+
- Dependencies listed in `requirements.txt`

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/monk-coder/test-task-traektory.git
   cd test-task-traektory
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Program
To run the program, use the following command:
```bash
python main.py
```

You can also use command line options to check specific time slots or find free slots. Here are the available options
#### Check a specific time slot:
```bash
python main.py -c "YYYY-MM-DD HH:MM-HH:MM"
```
For example, to check a slot from 10:00 to 12:00 on January 1, 2026:
```bash
python main.py -c "2026-01-01 10:00-12:00"
```
#### Show all busy slots:
```bash
python main.py -b
```
#### Find a free slot on a specific date:
```bash
python main.py -f "YYYY-MM-DD"
```
For example, to find a free slot on January 1, 2026:

```bash
python main.py -f "2023-10-01"
```
#### Show all free slots for a specific duration:
```bash
python main.py -d "HH:MM"
```
For example, to find all free slots for 1 hour:
```bash
python main.py -d "01:00"
```


## Running Tests
To run the tests, use `pytest`:
```bash
pytest -ra -q tests/
```
Ensure all dependencies are installed before running the tests.
