import os
import json
# We import the UserInterface to keep the logic (App) separate from the visual display (UI).
from interfaces.user_cli import UserInterface
# New Import: Bringing in the AdminInterface to handle Employee logic separately.
from interfaces.admin_cli import AdminInterface

class SaudiTravelApp:
    def __init__(self):
        # We define specific folders for data and recommendations to make the system modular. 
        self.data_folder = 'data'
        self.reviews_folder = 'recommendations'
        self.cities = []
        self.ui = UserInterface()
        # Initialize the AdminInterface by passing the data folder and UI tools.
        self.admin = AdminInterface(self.data_folder, self.ui)
        
        # Self-Healing: We ensure all necessary directories exist before the app starts.
        self.ensure_directories()

    def ensure_directories(self):
        """
        By creating missing folders automatically, we provide a 'Zero-Config' 
        experience for the user or developer setting up the app.
        """
        for folder in [self.data_folder, self.reviews_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def load_data(self):
        """
        Why this logic? To ensure the system is 'Self-Healing'.
        It filters out corrupted files and only loads valid city structures.
        """
        self.cities = [] 
        
        # Reloading data ensures that any changes made by the Admin 
        # are instantly reflected in the Tourist experience.
        files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        
        for file in files:
            path = os.path.join(self.data_folder, file)
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    # Integrity check: Ensure required keys exist to prevent UI crashes.
                    if isinstance(data, dict) and 'name' in data and 'id' in data:
                        self.cities.append(data)
                    else:
                        print(f"⚠️ Skipping {file}: Missing core 'name' or 'id' keys.")
                except json.JSONDecodeError:
                    print(f"⚠️ Warning: {file} is corrupted. Skipping.")
        
        return True if self.cities else False

    def start_system(self):
        """
        The Entry Point: This acts as the 'Router'. 
        It manages the user's journey based on their identity and needs.
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
                # Tourist Path: Reload data to ensure the most recent updates are visible.
                if self.load_data():
                    self.ui.run_user_experience(self.cities)
                else:
                    print("\n⚠️ Database Empty: No valid city files found in 'data/'.")
                    print("💡 Tip: Log in as Employee to register new destinations.")
                    input("\nPress Enter to return...")
            
            elif choice_idx == 1: 
                # Employee Path: Redirect to the new multi-function Admin Hub.
                # This now includes Authentication, Create, Update, and Delete functions.
                self.admin.manage_data()
                
            elif choice_idx == 2: 
                print("\n🌟 Thank you for visiting Saudi Arabia! Safe travels.")
                break

# The main block ensures this script only runs when executed directly.
if __name__ == "__main__":
    app = SaudiTravelApp()
    app.start_system()