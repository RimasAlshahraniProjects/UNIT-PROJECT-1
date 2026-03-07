import os
import json
import time

class AdminInterface:
    def __init__(self, data_folder, ui_tools):
        self.data_folder = data_folder
        self.ui = ui_tools
        self.reviews_folder = 'recommendations'
        self.admin_password = "saudi2030" 
        
        try:
            # Create the recommendations folder if it does not exist
            if not os.path.exists(self.reviews_folder):
                os.makedirs(self.reviews_folder)
        except Exception as e:
            print(f"❌ Startup Error: {e}")

    def get_validated_input(self, prompt, expected_type="text"):
        """
        Validates user input to prevent empty strings or numbers in text fields.
        """
        while True:
            try:
                user_input = input(prompt).strip()
                
                if not user_input:
                    print("⚠️ Error: Field cannot be empty.")
                    continue

                if expected_type == "text_only":
                    # Check if the input contains any digits
                    if any(char.isdigit() for char in user_input):
                        raise ValueError("Numbers are NOT allowed in this field.")
                    return user_input
                
                return user_input

            except ValueError as ve:
                print(f"⚠️ Validation Error: {ve}")
            except Exception as e:
                print(f"⚠️ Input Error: {e}")

    def authenticate(self):
        # Handle admin login with a password check
        self.ui.clear_screen()
        self.ui.show_header("Admin Access Control")
        attempts = 3
        while attempts > 0:
            password = input(f"🔑 Password ({attempts} left): ").strip()
            if password == self.admin_password:
                print("\n✅ Access Granted!")
                time.sleep(0.5)
                return True
            else:
                attempts -= 1
                print(f"❌ Incorrect Password.")
        return False

    def register_new_city(self):
        # Register a new city and create its data and review files
        self.ui.clear_screen()
        self.ui.show_header("Register New City")
        
        # Early check: Get the name and verify if it exists immediately
        name = self.get_validated_input("📍 City Name: ", "text_only")
        
        city_id = name.lower().replace(" ", "_")
        file_path = os.path.join(self.data_folder, f"{city_id}.json")
        
        if os.path.exists(file_path):
            print(f"\n⚠️ Conflict: City '{name}' is already registered in the system.")
            input("Press Enter to return to menu...")
            return

        # Proceed with details only if the city is new
        print("\n🌍 Enter Terrain Types:")
        print("💡 (e.g., Coastal, Mountain, Desert, Urban, Rural)")
        print("💡 Tip: Use commas to separate multiple types.")
        
        raw_terrains = self.get_validated_input("👉 Terrain(s): ", "text_only")
        # Split the input string into a list and capitalize each item
        terrain_list = [t.strip().capitalize() for t in raw_terrains.split(',')]

        short_desc = self.get_validated_input("📝 Short Desc: ", "text_only")
        full_desc  = self.get_validated_input("📖 Full Desc: ", "text_only")
        best_time  = self.get_validated_input("📅 Best Time: ", "text_only")

        reviews_path = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")

        try:
            # Create a new review placeholder for the city
            with open(reviews_path, 'w', encoding='utf-8') as rf:
                json.dump([], rf)

            new_city_data = {
                "id": city_id,
                "name": name,
                "terrain": terrain_list,
                "climate": "Moderate",
                "average_rating": "5.0",
                "short_description": short_desc,
                "full_description": full_desc,
                "best_time_to_visit": best_time,
                "activities_data": {},
                "travel_tips": ["Carry ID at all times."]
            }
            self.save_json(file_path, new_city_data)
        except Exception as e:
            print(f"❌ Critical Error: {e}")

    def save_json(self, path, data):
        # Save dictionary data into a JSON file with proper formatting
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("\n✅ System Synchronized Successfully.")
        except Exception as e:
            print(f"❌ Disk Save Error: {e}")
        input("Press Enter to continue...")

    def manage_data(self):
        # Main menu for administrative tasks
        if not self.authenticate(): return
        while True:
            self.ui.clear_screen()
            self.ui.show_header("Admin: Data Management")
            print("1- Register New City\n2- Add Category/Activity\n3- Delete Control\n4- Back")
            
            choice = self.ui.get_number_choice(4)
            if choice == 0: self.register_new_city()
            elif choice == 1: self.sub_menu_add()
            elif choice == 2: self.delete_data_menu()
            else: break

    def select_existing_city(self):
        # Lists all city files and allows the user to select one
        try:
            files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
            if not files:
                print("⚠️ Database is empty."); return None, None
            
            print("\nSelect City:")
            for i, f in enumerate(files, 1):
                print(f"{i}- {f.replace('.json', '').title()}")
            
            idx = self.ui.get_number_choice(len(files))
            file_path = os.path.join(self.data_folder, files[idx])
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f), file_path
        except Exception as e:
            print(f"❌ Loading Error: {e}")
            return None, None

    def sub_menu_add(self):
        # Menu for adding categories or activities to a city
        self.ui.clear_screen()
        self.ui.show_header("Update Data")
        print("1- New Category\n2- New Activity\n3- Cancel")
        choice = self.ui.get_number_choice(3)
        if choice == 0: self.add_new_category()
        elif choice == 1: self.add_new_activity()

    def add_new_category(self):
        # Add a new activity category to an existing city
        city_data, file_path = self.select_existing_city()
        if not city_data: return
        new_cat = self.get_validated_input("📁 New Category Name: ", "text_only")
        if new_cat in city_data["activities_data"]:
            print("⚠️ Already exists.")
        else:
            city_data["activities_data"][new_cat] = []
            self.save_json(file_path, city_data)

    def add_new_activity(self):
        # Add a specific activity to a selected category
        city_data, file_path = self.select_existing_city()
        if not city_data or not city_data["activities_data"]:
            print("⚠️ No categories found."); input("Enter..."); return

        cats = list(city_data["activities_data"].keys())
        for i, c in enumerate(cats, 1): print(f"{i}- {c}")
        c_idx = self.ui.get_number_choice(len(cats))
        
        new_act = {
            "name": self.get_validated_input("📍 Activity Name: ", "text_only"),
            "vibe": self.get_validated_input("✨ Vibe: ", "text_only"),
            "budget": "Medium",
            "experience_summary": self.get_validated_input("📝 Summary: ", "text_only"),
            "local_tip": "Visit during the golden hour."
        }
        city_data["activities_data"][cats[c_idx]].append(new_act)
        self.save_json(file_path, city_data)

    def delete_data_menu(self):
        # Menu for deleting cities or specific categories
        self.ui.clear_screen()
        self.ui.show_header("Delete Control")
        print("1- Delete Entire City\n2- Delete Category\n3- Cancel")
        choice = self.ui.get_number_choice(3)
        if choice == 0: self.delete_entire_city()
        elif choice == 1: self.delete_category()

    def delete_entire_city(self):
        # Remove city data file and its corresponding reviews
        files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        if not files: return
        for i, f in enumerate(files, 1): print(f"{i}- {f.replace('.json', '').title()}")
        idx = self.ui.get_number_choice(len(files))
        city_id = files[idx].replace('.json', '')
        
        confirm = input(f"⚠️ Delete {city_id} FOREVER? (yes/no): ").lower()
        if confirm == 'yes':
            try:
                os.remove(os.path.join(self.data_folder, files[idx]))
                rev = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")
                if os.path.exists(rev): os.remove(rev)
                print("🗑️ Files Deleted.")
            except Exception as e: print(f"❌ Error: {e}")
            input("Press Enter...")
            
    def delete_category(self):
        # Delete a specific activity category from city data
        city_data, file_path = self.select_existing_city()
        if not city_data: return
        cats = list(city_data["activities_data"].keys())
        if not cats: return
        for i, c in enumerate(cats, 1): print(f"{i}- {c}")
        idx = self.ui.get_number_choice(len(cats))
        del city_data["activities_data"][cats[idx]]
        self.save_json(file_path, city_data)