from playwright.async_api import async_playwright
from typing import Literal
import json
import os


def get_data(type: Literal['create', 'edit', 'delete']):
    file_path = os.path.join(os.path.dirname(__file__), 'data.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get(type, [])
    except FileNotFoundError:
        print(f"❌ File {file_path} not found.")
        raise
    except json.JSONDecodeError:
        print(f"❌ Error decoding JSON from {file_path}.")
        raise
