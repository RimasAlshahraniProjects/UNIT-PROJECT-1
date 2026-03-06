
from config.settings import ADMIN_PASSWORD, MAX_LOGIN_ATTEMPTS
from core.services_manager import (
    create_category,
    add_service,
    delete_service,
    get_services_by_category,
    get_all_categories
)


def check_admin_access():
    """Check admin password with limited attempts"""
    attempts = 0

    while attempts < MAX_LOGIN_ATTEMPTS:
        password = input("Enter admin password: ").strip()

        if password == ADMIN_PASSWORD:
            return True

        attempts += 1
        print(f"Wrong password! Attempts left: {MAX_LOGIN_ATTEMPTS - attempts}")

    print("Too many failed attempts. Try again later.")
    return False


def admin_menu():
    if not check_admin_access():
        return

    while True:
        print("\n=== Admin Control Panel ===")
        print("1 - Create New Category")
        print("2 - Add Service to Existing Category")
        print("3 - Delete Service")
        print("4 - View Services by Category")
        print("5 - Exit")

        choice = input("Choose an option: ").strip()

        match choice:

            case "1":
                category = input("Enter new category name: ").strip()
                success, message = create_category(category)
                print(message)

            case "2":
                categories = get_all_categories()
                if not categories:
                    print("No categories available.")
                    continue

                print("\nAvailable Categories:")
                for cat in categories:
                    print(f"- {cat}")

                category = input("Choose category: ").strip()
                name = input("Enter service name: ").strip()
                value = input("Enter service link or number: ").strip()

                success, message = add_service(category, name, value)
                print(message)

            case "3":
                category = input("Enter category: ").strip()
                name = input("Enter service name to delete: ").strip()

                confirm = input("Are you sure? (yes/no): ").lower()
                if confirm == "yes":
                    success, message = delete_service(category, name)
                    print(message)
                else:
                    print("Deletion cancelled.")

            case "4":
                category = input("Enter category to view: ").strip()
                services = get_services_by_category(category)

                if services:
                    print(f"\n--- {category} ---")
                    for s_name, details in services.items():
                        print(f"{s_name} → {details['value']} (Added: {details['created_at']})")
                else:
                    print("No services found.")

            case "5":
                print("Exiting Admin Panel...")
                break

            case _:
                print("Invalid choice.")


