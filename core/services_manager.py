# core/services_manager.py

import json
import os
from datetime import datetime
from config.settings import DATA_FILE_PATH


def load_services():
    """Load all services from JSON file"""
    if not os.path.exists(DATA_FILE_PATH):
        return {}

    with open(DATA_FILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_services(data):
    """Save services to JSON file"""
    with open(DATA_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def create_category(category_name):
    """Create a new category if it does not exist"""
    data = load_services()

    if category_name in data:
        return False, "Category already exists."

    data[category_name] = {}
    save_services(data)
    return True, f"Category '{category_name}' created successfully."


def add_service(category, name, value):
    """Add a service under existing category"""
    data = load_services()

    if category not in data:
        return False, "Category does not exist."

    if name in data[category]:
        return False, "Service already exists in this category."

    data[category][name] = {
        "value": value,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_services(data)
    return True, f"Service '{name}' added successfully."


def delete_service(category, name):
    """Delete a service from a category"""
    data = load_services()

    if category not in data:
        return False, "Category does not exist."

    if name not in data[category]:
        return False, "Service not found."

    del data[category][name]
    save_services(data)
    return True, f"Service '{name}' deleted successfully."


def get_services_by_category(category):
    """Return all services under a category"""
    data = load_services()
    return data.get(category, {})


def get_all_categories():
    """Return list of all categories"""
    data = load_services()
    return list(data.keys())