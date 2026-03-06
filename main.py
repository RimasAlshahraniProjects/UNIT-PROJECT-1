import os
import json
# Importing the UserInterface class from our custom module
from interfaces.user_cli import UserInterface

class SaudiTravelApp:
    def __init__(self):
        """
        Constructor: Initializes the application settings.
        Sets the data folder path and creates an instance of the UI.
        """
        self.data_folder = 'data'
        self.cities = []
        self.ui = UserInterface()

    def load_data(self):
        """
        Dynamic Data Loading: Reads all JSON files from the 'data' folder.
        This approach avoids hard-coding city names and allows the app to scale.
        """
        self.cities = [] # Reset the list to ensure data is fresh
        
        # Check if the data directory exists to prevent runtime errors
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            return False
        
        # Iterate through all files in the 'data' directory
        for file in os.listdir(self.data_folder):
            if file.endswith('.json'):
                path = os.path.join(self.data_folder, file)
                # Opening files with utf-8 encoding to support Arabic text
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        self.cities.append(json.load(f))
                    except json.JSONDecodeError:
                        print(f"⚠️ Warning: Failed to decode {file}. Skipping...")
        
        # Return True if cities were loaded, False otherwise
        return True if self.cities else False

    def start_system(self):
        """
        The Master Controller: Manages the main menu and directs users 
        based on their role (Tourist or Employee).
        """
        while True:
            self.ui.clear_screen()
            self.ui.show_header("Saudi Tourism System Console")
            
            print("Welcome! Please identify your role to proceed:")
            print("1. Tourist (Traveler Experience)")
            print("2. Employee (Admin Dashboard)")
            print("3. Exit System")
            
            # Using our custom validation function to handle user input
            choice_idx = self.ui.get_number_choice(3) 

            if choice_idx == 0: # Option 1: Tourist
                # Reload data every time a tourist enters to get the latest updates
                if self.load_data():
                    self.ui.run_user_experience(self.cities)
                else:
                    print("\n⚠️ System Error: No destination data found.")
                    print("Please ensure JSON files exist in the 'data/' folder.")
                    input("\nPress Enter to return to Main Menu...")
            
            elif choice_idx == 1: # Option 2: Admin/Employee
                self.admin_placeholder()
                
            elif choice_idx == 2: # Option 3: Exit
                print("\n🌟 Thank you for visiting Saudi Arabia! Safe travels.")
                break

    def admin_placeholder(self):
        """Temporary placeholder for the Admin module."""
        self.ui.clear_screen()
        self.ui.show_header("Admin Dashboard")
        print("\n🛠️ Admin Logic (Add/Edit Destinations) is under development.")
        print("This module will allow employees to update the city database.")
        input("\nPress Enter to return to main menu...")

# Execution point of the application
if __name__ == "__main__":
    app = SaudiTravelApp()
    app.start_system()