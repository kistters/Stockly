import json
from datetime import datetime, date
from pathlib import Path


def day(input_date: str) -> date:
    return datetime.strptime(input_date, '%Y-%m-%d').date()


def load_file(filename) -> str:
    file_path = Path(__file__).parent / 'files' / filename
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def load_json(filename) -> dict:
    return json.loads(load_file(filename))