import os
import json
import time

class AdminInterface:
    def __init__(self, data_folder, ui_tools):
        self.data_folder = data_folder
        self.ui = ui_tools
        # We also need a reference to the reviews folder to sync deletions and creations.
        self.reviews_folder = 'recommendations'
        self.admin_password = "saudi2030" 
        
        # Ensure the recommendations directory exists so the admin can write to it.
        if not os.path.exists(self.reviews_folder):
            os.makedirs(self.reviews_folder)

    def authenticate(self):
        """
        Why Authentication? To ensure that sensitive data operations 
        (like adding new destinations) are only performed by authorized staff.
        """
        self.ui.clear_screen()
        self.ui.show_header("Admin Access Control")
        
        attempts = 3
        while attempts > 0:
            password = input(f"🔑 Enter Admin Password ({attempts} attempts left): ").strip()
            
            if password == self.admin_password:
                print("\n✅ Access Granted!")
                time.sleep(1)
                return True
            else:
                attempts -= 1
                if attempts > 0:
                    print(f"❌ Incorrect Password. Try again.")
        
        print("\n⚠️ Access Denied: Too many failed attempts.")
        input("Press Enter to return to main menu...")
        return False

    def manage_data(self):
        if not self.authenticate():
            return

        while True:
            self.ui.clear_screen()
            self.ui.show_header("Admin: Data Management")
            print("What would you like to do?")
            print("1- Register a New City (Create JSON)")
            print("2- Add a Category/Activity to an existing city")
            print("3- DELETE Data (City, Category, or Activity)")
            print("4- Back to Main Menu")

            choice = self.ui.get_number_choice(4)

            if choice == 0:
                self.register_new_city()
            elif choice == 1:
                self.sub_menu_add()
            elif choice == 2:
                self.delete_data_menu()
            else:
                break

    # --- SECTION: CREATE (New City) ---
    def register_new_city(self):
        self.ui.clear_screen()
        self.ui.show_header("Register New City")
        name = input("📍 City Name: ").strip()
        if not name: return
        
        city_id = name.lower().replace(" ", "_")
        file_path = os.path.join(self.data_folder, f"{city_id}.json")
        # --- SYNC: Prepare the review file path ---
        reviews_path = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")
        
        if os.path.exists(file_path):
            print("⚠️ This city already exists in the database!")
            input("Press Enter to continue...")
            return

        # Initialize the city review file with an empty list.
        # This ensures the User Interface won't crash when searching for new city reviews.
        with open(reviews_path, 'w', encoding='utf-8') as rf:
            json.dump([], rf)

        new_city_data = {
            "id": city_id,
            "name": name,
            "terrain": [input("🌍 Terrain (e.g., Coastal, Mountain): ").strip()],
            "climate": "Moderate",
            "average_rating": "5.0",
            "short_description": input("📝 Short Description: ").strip(),
            "full_description": input("📖 Full Description: ").strip(),
            "best_time_to_visit": input("📅 Best Time to Visit: ").strip(),
            "activities_data": {},
            "travel_tips": ["Carry your ID at all times."]
        }
        self.save_json(file_path, new_city_data)

    # --- SECTION: UPDATE (Add Category/Activity) ---
    def sub_menu_add(self):
        self.ui.clear_screen()
        self.ui.show_header("Add Details to Existing City")
        print("1- Add a New Category (e.g., Nature, Shopping)")
        print("2- Add a New Activity to an existing category")
        print("3- Cancel")
        
        choice = self.ui.get_number_choice(3)
        if choice == 0: self.add_new_category()
        elif choice == 1: self.add_new_activity()

    def add_new_category(self):
        city_data, file_path = self.select_existing_city()
        if not city_data: return

        new_cat = input("📁 Enter New Category Name: ").strip()
        if new_cat in city_data["activities_data"]:
            print("⚠️ Category already exists!")
        else:
            city_data["activities_data"][new_cat] = []
            self.save_json(file_path, city_data)

    def add_new_activity(self):
        city_data, file_path = self.select_existing_city()
        if not city_data: return

        categories = list(city_data["activities_data"].keys())
        if not categories:
            print("⚠️ No categories found. Please add a category first.")
            input("Press Enter..."); return

        print("\nSelect Category:")
        for i, cat in enumerate(categories, 1): print(f"{i}- {cat}")
        cat_idx = self.ui.get_number_choice(len(categories))
        selected_cat = categories[cat_idx]

        new_act = {
            "name": input("📍 Activity Name: "),
            "vibe": input("✨ Vibe: "),
            "budget": "Medium",
            "experience_summary": input("📝 Summary: "),
            "local_tip": "Check opening hours before visiting."
        }
        
        city_data["activities_data"][selected_cat].append(new_act)
        self.save_json(file_path, city_data)

    # --- SECTION: DELETE ---
    def delete_data_menu(self):
        self.ui.clear_screen()
        self.ui.show_header("Delete Data Control")
        print("1- Delete an Entire City (Permanent)")
        print("2- Delete a Category from a city")
        print("3- Delete a Specific Activity")
        print("4- Cancel")

        choice = self.ui.get_number_choice(4)
        if choice == 0: self.delete_entire_city()
        elif choice == 1: self.delete_category()
        elif choice == 2: self.delete_activity()

    def delete_entire_city(self):
        files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        if not files: return
        
        print("\nSelect City to DELETE:")
        for i, f in enumerate(files, 1): print(f"{i}- {f.replace('.json', '').title()}")
        idx = self.ui.get_number_choice(len(files))
        
        city_id = files[idx].replace('.json', '')
        file_path = os.path.join(self.data_folder, files[idx])
        # --- SYNC: Review file must be deleted too ---
        reviews_path = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")
        
        confirm = input(f"⚠️ Are you sure you want to delete {files[idx]}? (yes/no): ").lower()
        if confirm == 'yes':
            # Remove core data
            if os.path.exists(file_path):
                os.remove(file_path)
            # Remove linked reviews to maintain database integrity
            if os.path.exists(reviews_path):
                os.remove(reviews_path)
                
            print(f"🗑️ {city_id.title()} and its reviews deleted successfully.")
            input("Press Enter to continue...")

    def delete_category(self):
        city_data, file_path = self.select_existing_city()
        if not city_data: return

        categories = list(city_data["activities_data"].keys())
        if not categories: return

        print("\nSelect Category to DELETE:")
        for i, cat in enumerate(categories, 1): print(f"{i}- {cat}")
        idx = self.ui.get_number_choice(len(categories))
        selected_cat = categories[idx]

        confirm = input(f"⚠️ Delete ALL activities in '{selected_cat}'? (yes/no): ").lower()
        if confirm == 'yes':
            del city_data["activities_data"][selected_cat]
            self.save_json(file_path, city_data)

    def delete_activity(self):
        city_data, file_path = self.select_existing_city()
        if not city_data: return

        categories = list(city_data["activities_data"].keys())
        if not categories: return

        print("\nSelect Category:")
        for i, cat in enumerate(categories, 1): print(f"{i}- {cat}")
        cat_idx = self.ui.get_number_choice(len(categories))
        selected_cat = categories[cat_idx]

        activities = city_data["activities_data"][selected_cat]
        if not activities: 
            print("No activities to delete."); input("Enter..."); return

        print("\nSelect Activity to DELETE:")
        for i, act in enumerate(activities, 1): print(f"{i}- {act['name']}")
        act_idx = self.ui.get_number_choice(len(activities))
        
        del city_data["activities_data"][selected_cat][act_idx]
        self.save_json(file_path, city_data)

    # --- SECTION: HELPERS ---
    def select_existing_city(self):
        files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        if not files: 
            print("No cities found."); input("Enter..."); return None, None
        
        print("\nSelect City:")
        for i, f in enumerate(files, 1): print(f"{i}- {f.replace('.json', '').title()}")
        city_idx = self.ui.get_number_choice(len(files))
        file_path = os.path.join(self.data_folder, files[city_idx])
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f), file_path

    def save_json(self, path, data):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("\n✅ Database Updated Successfully!")
        except Exception as e:
            print(f"\n❌ Failed to save: {e}")
        input("Press Enter to continue...")