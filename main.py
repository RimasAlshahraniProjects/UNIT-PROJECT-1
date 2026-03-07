import os
import json
# Import the UserInterface to keep the logic (App) separate from the visual display (UI).
from interfaces.user_cli import UserInterface
# Import the AdminInterface to handle Employee logic separately.
from interfaces.admin_cli import AdminInterface

class SaudiTravelApp:
    def __init__(self):
        # Define specific folders for data and recommendations to keep the system modular. 
        self.data_folder = 'data'
        self.reviews_folder = 'recommendations'
        self.cities = []
        self.ui = UserInterface()
        # Initialize the AdminInterface with the required data path and UI tools.
        self.admin = AdminInterface(self.data_folder, self.ui)
        
        # Ensure all necessary directories exist when the application starts.
        self.ensure_directories()

    def ensure_directories(self):
        """
        Creates missing folders automatically to provide a 'Zero-Config' experience.
        """
        for folder in [self.data_folder, self.reviews_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def load_data(self):
        """
        Filters out corrupted files and loads only valid city data structures.
        """
        self.cities = [] 
        
        # Check if the data folder exists or if it is empty before proceeding.
        if not os.path.exists(self.data_folder) or not os.listdir(self.data_folder):
            return False

        files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        
        for file in files:
            path = os.path.join(self.data_folder, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # --- Data Integrity & Self-Healing ---
                    # Recreates the review file if it is missing for an existing city.
                    city_id = data.get('id')
                    if city_id:
                        review_path = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")
                        if not os.path.exists(review_path):
                            with open(review_path, 'w', encoding='utf-8') as rf:
                                json.dump([], rf)
                    
                    # Verify core keys to prevent the UI from crashing during execution.
                    if isinstance(data, dict) and 'name' in data and 'id' in data:
                        self.cities.append(data)
                    else:
                        print(f"⚠️ Skipping {file}: Missing core 'name' or 'id' keys.")
            except (json.JSONDecodeError, IOError) as e:
                # Log the error and skip the file to prevent a full system crash.
                print(f"⚠️ Warning: {file} is corrupted. Skipping. Error: {e}")
        
        return True if self.cities else False

    def start_system(self):
        """
        Acts as the main router for the application based on user roles.
        """
        while True:
            self.ui.clear_screen()
            self.ui.show_header("Saudi Tourism System Console")
            
            print("Welcome! Please identify your role to proceed:")
            print("1. Tourist (Traveler Experience & Reviews)")
            print("2. Employee (Admin Dashboard & Data Sync)")
            print("3. Exit System")
            
            choice_idx = self.ui.get_number_choice(3) 

            if choice_idx == 0: 
                # Tourist Path: Load current data to reflect the latest admin updates.
                if self.load_data():
                    self.ui.run_user_experience(self.cities)
                else:
                    print("\n⚠️ Database Empty: No valid city files found in 'data/'.")
                    print("💡 Tip: Log in as Employee to register new destinations.")
                    input("\nPress Enter to return...")
            
            elif choice_idx == 1: 
                # Employee Path: Redirect to the Admin management module.
                self.admin.manage_data()
                
            elif choice_idx == 2: 
                print("\n🌟 Thank you for visiting Saudi Arabia! Safe travels.")
                break

# Ensure the app only runs if this script is executed directly.
if __name__ == "__main__":
    app = SaudiTravelApp()
    app.start_system()