import os
import json
from dotenv import load_dotenv  # Added: Library for security
from interfaces.user_cli import UserInterface
from interfaces.admin_cli import AdminInterface
from rich import print as rprint

# Added: Load secrets from .env file immediately
load_dotenv()

class SaudiTravelApp:
    def __init__(self):
        """
        Initializes the application state and core dependencies.
        Maintains structural integrity through modular directory mapping.
        """
        self.data_folder = 'data'
        self.reviews_folder = 'recommendations'
        self.cities = []
        
        # Added: Fetch the password from the environment variables
        self.admin_password = os.getenv("ADMIN_PASSWORD")
        
        # Initialize UI first to use its methods (like clear_screen)
        self.ui = UserInterface()
        
        # Fixed: Pass the secret_password to match the updated AdminInterface
        self.admin = AdminInterface(self.data_folder, self.ui, self.admin_password)
        
        # Bootstrap: Ensure filesystem prerequisites are met
        self.ensure_directories()
        
        # Initial data load to populate the system on startup
        self.load_data()

    def ensure_directories(self):
        """Zero-Config Setup: Automatically generates required infrastructure."""
        for folder in [self.data_folder, self.reviews_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def load_data(self):
        """
        Data Integrity Layer: Implements a 'Self-Healing' mechanism.
        Returns True if at least one valid city is loaded.
        """
        self.cities = [] 
        
        if not os.path.exists(self.data_folder):
            return False

        files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        
        for file in files:
            path = os.path.join(self.data_folder, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # --- Automated Recovery for Reviews ---
                    city_id = data.get('id')
                    if city_id:
                        review_path = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")
                        if not os.path.exists(review_path):
                            with open(review_path, 'w', encoding='utf-8') as rf:
                                json.dump([], rf)
                    
                    # Schema Validation: Ensuring core keys exist
                    if isinstance(data, dict) and 'name' in data and 'id' in data:
                        self.cities.append(data)
            except (json.JSONDecodeError, IOError):
                continue # Skip corrupted files silently to maintain flow
        
        return len(self.cities) > 0

    def start_system(self):
        """
        Main Router: Dispatches requests to specialized experience flows.
        """
        while True:
            self.ui.clear_screen()
            self.ui.show_header("SaudiExplorer Hub")
            
            rprint("\n[bold white]Welcome to the Kingdom,[/] [italic green]where heritage meets the future.[/]")
            rprint("[dim white]How would you like to proceed today?[/]")
            
            rprint("\n [bold green]1.[/] [white]Traveler Experience[/] [dim green](Explore destinations)[/]")
            rprint(" [bold green]2.[/] [white]System Management[/] [dim green](Administrative access)[/]")
            rprint(" [bold white]3.[/] [white]Exit Explorer[/]")
            
            # Use the robust validation method from UserInterface
            choice_idx = self.ui.get_number_choice(3) 

            if choice_idx == 0: 
                # Traveler Flow: Reload data to ensure updates are captured
                if self.load_data():
                    self.ui.run_user_experience(self.cities)
                else:
                    self.ui.clear_screen()
                    self.ui.show_header("Notice")
                    rprint("\n[bold white]The destination database is currently empty.[/]")
                    rprint("[italic green]Please use the Management portal to add new destinations.[/]")
                    input("\nPress Enter to return...")
            
            elif choice_idx == 1: 
                # Admin Flow: Redirect to specialized admin interface
                self.admin.manage_data()
                # Crucial: Re-sync local state immediately after admin exit
                self.load_data() 
                
            elif choice_idx == 2: 
                self.ui.clear_screen()
                rprint("\n[bold white]It was a pleasure serving you today.[/]")
                rprint("[bold green]Until we meet again, safe travels! 🇸🇦[/]\n")
                break

if __name__ == "__main__":
    app = SaudiTravelApp()
    app.start_system()