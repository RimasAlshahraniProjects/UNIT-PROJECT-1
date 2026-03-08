import os
import json
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print as rprint

console = Console()

class AdminInterface:
    def __init__(self, data_folder, ui_tools):
        self.data_folder = data_folder
        self.ui = ui_tools
        self.reviews_folder = 'recommendations'
        self.admin_password = "saudi2030" 
        
        # Ensure the recommendations directory exists
        if not os.path.exists(self.reviews_folder):
            os.makedirs(self.reviews_folder)

    def get_validated_input(self, prompt, expected_type="text"):
        """Handles user input with validation and consistent styling."""
        while True:
            user_input = console.input(f"[bold green]>[/] [white]{prompt}[/]").strip()
            
            if not user_input:
                rprint("[dim white]Required field. Please enter data.[/]")
                continue

            if expected_type == "text_only":
                if any(char.isdigit() for char in user_input):
                    rprint("[dim white]Error: Numbers are not permitted in this field.[/]")
                    continue
            return user_input

    def authenticate(self):
        """Standard login security check."""
        self.ui.clear_screen()
        self.ui.show_header("Administrative Security")
        attempts = 3
        while attempts > 0:
            password = console.input(f"\n[bold white]Key Passcode ({attempts} left): [/]").strip()
            if password == self.admin_password:
                rprint("\n[bold green]Success: Identity Verified. Access Granted.[/]")
                time.sleep(1)
                return True
            else:
                attempts -= 1
                rprint(f"[bold red]Access Denied. Verification Failed.[/]")
        return False

    def manage_data(self):
        """Main Admin menu with simplified action verbs."""
        if not self.authenticate(): return
        while True:
            self.ui.clear_screen()
            self.ui.show_header("Admin: Command Center")
            
            menu_text = Text()
            menu_text.append("1. Add New City\n", style="bold white")
            menu_text.append("2. Update Activities or Categories\n", style="bold white")
            menu_text.append("3. Delete Cities or Data\n", style="bold white")
            menu_text.append("4. Close Admin Panel", style="dim white")
            
            rprint(Panel(menu_text, title="[bold green]Management Menu[/]", border_style="green"))
            
            choice = self.ui.get_number_choice(4)
            if choice == 0: self.register_new_city()
            elif choice == 1: self.sub_menu_add()
            elif choice == 2: self.delete_data_menu()
            else: break

    def register_new_city(self):
        """Flow for adding a new city destination to the system."""
        self.ui.clear_screen()
        self.ui.show_header("Registry: New City")
        
        name = self.get_validated_input("Official City Name: ", "text_only")
        city_id = name.lower().replace(" ", "_")
        file_path = os.path.join(self.data_folder, f"{city_id}.json")
        
        if os.path.exists(file_path):
            rprint(f"\n[bold yellow]Record Exists: {name} is already registered.[/]")
            input("Press Enter...")
            return

        # Terrain input (flexible text input, cleaned into a list)
        rprint("\n[bold white]Terrain Profile:[/]")
        rprint("[dim white](Separate multiple types with commas, e.g.: Coastal, Urban, Heritage)[/]")
        raw_terrains = self.get_validated_input("Enter Terrains: ")
        # Remove parentheses if entered and split by comma
        terrain_list = [t.strip().capitalize() for t in raw_terrains.replace('(', '').replace(')', '').split(',')]

        climate = self.get_validated_input("Climate (e.g., Warm / Mild Winter): ")

        rprint("\n[bold white]Narrative Details:[/]")
        short_desc = self.get_validated_input("Short Description (Headline): ")
        full_desc  = self.get_validated_input("Full Description (The Story): ")
        best_time  = self.get_validated_input("Best Time to Visit (e.g., October to April): ")

        # Create the data dictionary matching the required JSON structure
        new_city_data = {
            "id": city_id,
            "name": name,
            "terrain": terrain_list,
            "climate": climate,
            "coastal": any("Coast" in t for t in terrain_list),
            "mountainous": any("Mountain" in t for t in terrain_list),
            "average_rating": 5.0,
            "best_time_to_visit": best_time,
            "short_description": short_desc,
            "full_description": full_desc,
            "activities_data": {},
            "travel_tips": ["Standard safety protocols apply."]
        }
        
        # Automatically generate a linked reviews file
        reviews_path = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")
        with open(reviews_path, 'w', encoding='utf-8') as rf:
            json.dump([], rf)

        self.save_json(file_path, new_city_data)

    def save_json(self, path, data):
        """Synchronizes data with the local JSON database."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            rprint("\n[bold green]Status: Repository Updated Successfully.[/]")
        except Exception:
            rprint("\n[bold red]Critical: Storage Sync Failure.[/]")
        input("\n[dim white]Press Enter to proceed...[/]")

    def select_existing_city(self):
        """Displays a table for selecting an existing city file."""
        files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        if not files:
            rprint("[bold yellow]Database Status: Empty.[/]"); return None, None
        
        table = Table(title="System Registry", border_style="green", header_style="bold green")
        table.add_column("Ref", justify="center")
        table.add_column("Destination", style="white")
        
        for i, f in enumerate(files, 1):
            table.add_row(str(i), f.replace('.json', '').title())
        
        console.print(table)
        idx = self.ui.get_number_choice(len(files))
        file_path = os.path.join(self.data_folder, files[idx])
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f), file_path

    def sub_menu_add(self):
        """Routing for adding content to specific cities."""
        self.ui.clear_screen()
        self.ui.show_header("Update Content")
        rprint("[bold white]1.[/] Create Category\n[bold white]2.[/] Add Activity\n[bold dim white]3.[/] Exit")
        choice = self.ui.get_number_choice(3)
        if choice == 0: self.add_new_category()
        elif choice == 1: self.add_new_activity()

    def add_new_category(self):
        city_data, file_path = self.select_existing_city()
        if not city_data: return
        new_cat = self.get_validated_input("New Category Title: ", "text_only").lower().replace(" ", "_")
        
        if new_cat in city_data["activities_data"]:
            rprint("[bold yellow]Notification: Category already exists.[/]")
            input("Enter...")
        else:
            city_data["activities_data"][new_cat] = []
            self.save_json(file_path, city_data)

    def add_new_activity(self):
        city_data, file_path = self.select_existing_city()
        if not city_data or not city_data["activities_data"]:
            rprint("[bold yellow]Missing: Please create a category first.[/]"); input("Enter..."); return

        cats = list(city_data["activities_data"].keys())
        for i, c in enumerate(cats, 1): rprint(f"[bold green]{i}.[/] {c.title()}")
        c_idx = self.ui.get_number_choice(len(cats))
        
        rprint(f"\n[bold white]Adding Record to {cats[c_idx].title()}:[/]")
        new_act = {
            "name": self.get_validated_input("Location Name: "),
            "vibe": self.get_validated_input("Experience Vibe: "),
            "budget": self.get_validated_input("Budget Level: "),
            "signature_dish": self.get_validated_input("Must-Try Item: "),
            "top_activity": self.get_validated_input("Primary Activity: "),
            "nearby_cafe": self.get_validated_input("Local Cafe: "),
            "nearby_restaurant": self.get_validated_input("Local Restaurant: "),
            "local_tip": self.get_validated_input("Operational Tip: ")
        }
        city_data["activities_data"][cats[c_idx]].append(new_act)
        self.save_json(file_path, city_data)

    def delete_data_menu(self):
        """Routing for deletion operations."""
        self.ui.clear_screen()
        self.ui.show_header("Delete Protocol")
        rprint("[bold red]Warning: Deletion is permanent.[/]")
        rprint("[bold white]1.[/] Delete Entire City\n[bold white]2.[/] Delete Category\n[bold dim white]3.[/] Cancel")
        choice = self.ui.get_number_choice(3)
        if choice == 0: self.delete_entire_city()
        elif choice == 1: self.delete_category()

    def delete_entire_city(self):
        files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        if not files: return
        for i, f in enumerate(files, 1): rprint(f"{i}- {f.replace('.json', '').title()}")
        idx = self.ui.get_number_choice(len(files))
        city_id = files[idx].replace('.json', '')
        
        confirm = console.input(f"\n[bold red]Action Required: Type 'CONFIRM' to delete {city_id.upper()}: [/]")
        if confirm == 'CONFIRM':
            os.remove(os.path.join(self.data_folder, files[idx]))
            rev = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")
            if os.path.exists(rev): os.remove(rev)
            rprint("[bold green]Registry Cleared.[/]")
            input("Press Enter...")
            
    def delete_category(self):
        city_data, file_path = self.select_existing_city()
        if not city_data: return
        cats = list(city_data["activities_data"].keys())
        if not cats: rprint("[dim white]No records to delete.[/]"); input("Enter..."); return
        for i, c in enumerate(cats, 1): rprint(f"{i}- {c.title()}")
        idx = self.ui.get_number_choice(len(cats))
        del city_data["activities_data"][cats[idx]]
        self.save_json(file_path, city_data)