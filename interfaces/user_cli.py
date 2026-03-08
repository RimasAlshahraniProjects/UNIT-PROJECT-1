import os
import textwrap
import json
from rich.console import Console  # Styling: Core class for managing and rendering console output
from rich.panel import Panel      # Styling: Tool for enclosing text or objects within a bordered box
from rich.table import Table      # Styling: Tool for presenting data in a structured tabular format
from rich.columns import Columns  # Styling: Helper for displaying multiple items side-by-side
from rich.text import Text        # Styling: Class for advanced text styling (colors/fonts within a string)
from rich import print as rprint  # Styling: Enhanced print function (Aliased as 'rprint') to support Rich markup and cross-platform color rendering

console = Console()

class UserInterface:
    def __init__(self):
        """Initializes the traveler experience environment and validates directories."""
        self.reviews_folder = 'recommendations'
        if not os.path.exists(self.reviews_folder):
            os.makedirs(self.reviews_folder)

    def clear_screen(self):
        """Clears the terminal to maintain a clean workspace."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_header(self, title):
        """Renders the SaudiExplorer premium brand identity."""
        logo_text = Text()
        logo_text.append("🇸🇦 SAUDI\n", style="bold green")
        logo_text.append("EXPLORER", style="bold white") 

        title_text = Text()
        title_text.append(f" {title.upper()}\n", style="bold white")
        title_text.append("Your First Destination to Explore the Kingdom", style="italic green")

        header_columns = Columns([title_text, logo_text], expand=True)
        rprint(Panel(header_columns, border_style="green", padding=(1, 2)))

    def run_user_experience(self, all_cities):
        """Main entry point for international tourists."""
        self.clear_screen()
        self.show_header("Discovery Portal")
        
        welcome_msg = Text.assemble(
            ("\nWelcome to the Kingdom, where timeless heritage meets an inspiring future.\n", "bold white"),
            ("How would you like to begin your journey today?\n", "green")
        )
        rprint(Panel(welcome_msg, border_style="green"))
        
        rprint("\n[bold white]Journey Options:[/]")
        rprint(" [bold green]1.[/] Explore by Vibe (Guided Discovery)")
        rprint(" [bold green]2.[/] I Know My Destination (Direct Access)")
        
        path_choice = self.get_number_choice(2)
        if path_choice == 0:
            self.guided_discovery_flow(all_cities)
        else:
            self.direct_city_flow(all_cities)

    def show_post_selection_menu(self, city):
        """Detailed navigation menu for a specific city."""
        while True:
            self.clear_screen()
            self.show_header(f"Destination: {city['name']}")
            rprint(f"\n[bold white]What would you like to discover in {city['name']} [bold green]for today[/]?[/]")
            
            categories = list(city.get('activities_data', {}).keys())
            
            for idx, cat in enumerate(categories, 1):
                clean_name = cat.replace('_', ' ').capitalize()
                rprint(f" [bold green]{idx}.[/] {clean_name}")
            
            rprint(f" [bold green]{len(categories) + 1}.[/] Traveler Feedback & Stories")
            rprint(f" [bold white]{len(categories) + 2}.[/] Return to Main Hub")

            choice = self.get_number_choice(len(categories) + 2)

            if choice < len(categories):
                selected_cat = categories[choice]
                activities = city['activities_data'][selected_cat]
                self.display_category_details(city['name'], selected_cat, activities)
            elif choice == len(categories):
                self.show_reviews_portal(city)
            else:
                break

    def display_category_details(self, city_name, cat_name, activities):
        """Renders activity data in a clean, minimalist table without icons."""
        self.clear_screen()
        header_title = cat_name.replace('_', ' ').title()
        self.show_header(f"{header_title} | {city_name}")
        
        table = Table(
            title=f"[bold white]{header_title.upper()} EXPLORATION LOG[/]", 
            show_lines=True, 
            border_style="green",
            header_style="bold green",
            expand=True
        )
        
        table.add_column("Location & Vibe", style="bold white", width=25)
        table.add_column("Budget", justify="center", style="green")
        table.add_column("Must-Try", style="white", width=30)
        table.add_column("Nearby Spots", style="dim white")
        table.add_column("Expert Local Tip", style="italic green", width=35)

        for act in activities:
            loc_vibe = f"{act.get('name', 'N/A')}\n[dim]{act.get('vibe', 'Authentic Experience')}[/]"
            
            # Clean text instead of icons
            must_try = f"Dish: {act.get('signature_dish', 'N/A')}\nActivity: {act.get('top_activity', 'N/A')}"
            social = f"Cafe: {act.get('nearby_cafe', 'Nearby')}\nRest: {act.get('nearby_restaurant', 'Nearby')}"

            table.add_row(
                loc_vibe,
                act.get('budget', 'N/A'),
                must_try,
                social,
                act.get('local_tip', 'Enjoy the unique atmosphere.')
            )
            
        console.print(table)
        rprint("\n[dim white]Press Enter to return to city menu...[/]")
        input()

    def show_reviews_portal(self, city):
        """Interactive hub for reading and contributing traveler feedback."""
        while True:
            self.clear_screen()
            self.show_header(f"Traveler Stories: {city['name']}")
            
            city_id = city.get('id')
            review_file = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")
            reviews = []

            if os.path.exists(review_file):
                try:
                    with open(review_file, 'r', encoding='utf-8') as f:
                        reviews = json.load(f)
                except: pass

            if not reviews:
                rprint("[italic green]No shared experiences for this location yet.[/]")
            else:
                for r in reviews:
                    wrapped_comment = textwrap.fill(r.get('comment', ''), width=65)
                    # Simple clean panel for feedback
                    rprint(Panel(
                        wrapped_comment, 
                        title=f"[bold green]{r.get('sentiment', 'Positive')}[/]", 
                        subtitle=f"By {r.get('user')} ({r.get('nationality')} {r.get('type')})"
                    ))

            rprint("\n [bold green]1.[/] Share Your Story")
            rprint(" [bold white]2.[/] Back to City Menu")
            
            choice = input("\nSelect (1-2): ").strip()
            if choice == "1":
                self.add_new_review(city_id, review_file, reviews)
            else:
                break

    def add_new_review(self, city_id, file_path, existing_reviews):
        """Collects feedback with strict validation to ensure data quality."""
        self.clear_screen()
        self.show_header("Share Your Experience")
        rprint("[bold green]We value your journey![/] [white]Please provide valid details:[/]\n")
        
        while True:
            name = input("Full Name: ").strip()
            if len(name) >= 2: break
            rprint("[dim white]Error: Please enter a valid name (min. 2 chars).[/]")

        while True:
            nationality = input("Nationality: ").strip()
            if len(nationality) >= 3: break
            rprint("[dim white]Error: Please enter a valid nationality.[/]")

        while True:
            v_type = input("Are you a (Local) or (Tourist)? ").strip().capitalize()
            if v_type in ["Local", "Tourist"]: break
            rprint("[dim white]Error: Please type exactly 'Local' or 'Tourist'.[/]")
        
        rprint("\n[dim white]Your message for future explorers (Min. 5 characters):[/]")
        while True:
            comment = input("> ").strip()
            if len(comment) >= 5: break
            rprint("[dim white]Error: Your story is too short.[/]")

        sentiment = input("How was the vibe? (e.g., Magical, Modern): ").strip() or "Excellent"

        new_entry = {
            "city": city_id.capitalize(),
            "user": name,
            "nationality": nationality,
            "type": v_type,
            "comment": comment,
            "sentiment": sentiment
        }
        existing_reviews.append(new_entry)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_reviews, f, indent=4, ensure_ascii=False)
            
        rprint("\n[bold green]Success![/] Your story has been saved. 🇸🇦")
        input("\nPress Enter to return...")

    def get_number_choice(self, limit):
        """Standardized numeric input validation."""
        while True:
            try:
                user_input = input(f"\nSelect an option (1-{limit}): ").strip()
                choice = int(user_input)
                if 1 <= choice <= limit: return choice - 1
                rprint(f"[dim white]Selection out of range. Choose 1-{limit}.[/]")
            except ValueError:
                rprint("[dim white]Numerical input required.[/]")

    def direct_city_flow(self, all_cities):
        self.clear_screen()
        self.show_header("Destination Hub")
        rprint("\n[bold white]Select a city to explore:[/]")
        for idx, city in enumerate(all_cities, 1):
            rprint(f"  [bold green]{idx}.[/] {city.get('name')}")
        choice = self.get_number_choice(len(all_cities))
        self.show_post_selection_menu(all_cities[choice])

    def guided_discovery_flow(self, all_cities):
        self.clear_screen()
        self.show_header("Guided Discovery")
        valid_vibes = ["Coastal", "Mountain", "Desert", "Urban", "Oasis"]
        while True:
            rprint(f"\n[bold white]What vibe are you looking for?[/]")
            rprint(f"[green]({', '.join(valid_vibes)})[/]")
            t_choice = input("\nEnter terrain type (or leave blank for all): ").strip().capitalize()
            
            if t_choice and t_choice not in valid_vibes:
                rprint("[dim white]Invalid vibe. Please choose from the list.[/]")
                continue
                
            suitable = [c for c in all_cities if any(t_choice in terrain.capitalize() for terrain in c.get('terrain', []))]
            final_list = suitable if (suitable and t_choice != "") else all_cities
            
            for idx, city in enumerate(final_list, 1):
                rprint(f"  [bold green]{idx}.[/] {city.get('name')} | [dim white]{city.get('short_description', 'Explore the beauty.')}[/]")
            
            choice = self.get_number_choice(len(final_list))
            if self.confirm_selection(final_list[choice]):
                self.show_post_selection_menu(final_list[choice])
                break

    def confirm_selection(self, city):
        """Renders description and stats before final entry."""
        self.clear_screen()
        self.show_header(f"Discover {city.get('name')}")
        
        desc_panel = Panel(
            f"[white]{textwrap.fill(city.get('full_description', 'No description available.'), width=65)}[/]",
            title=f"[bold green]Global Rating: {city.get('average_rating', 'N/A')}/5[/]",
            subtitle=f"[white]Peak Season: {city.get('best_time_to_visit', 'Year-round')}[/]",
            border_style="green"
        )
        rprint(desc_panel)
        
        while True:
            confirm = input(f"\nExplore {city.get('name')}? (yes/no): ").strip().lower()
            if confirm in ["yes", "y"]: return True
            if confirm in ["no", "n"]: return False
            rprint("[dim white]Please enter 'yes' or 'no'.[/]")