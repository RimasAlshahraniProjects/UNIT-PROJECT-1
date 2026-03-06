import os

class UserInterface:
    def __init__(self):
        pass

    def clear_screen(self):
        """
        Clears the terminal screen to provide a clean and professional user interface.
        It checks the operating system: 'cls' for Windows (nt) and 'clear' for Mac/Linux.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_header(self, title):
        """عرض ترويسة مزينة للقسم الحالي"""
        print("\n" + "="*60)
        print(f"🌟 {title.upper()} 🌟")
        print("="*60)

    def get_number_choice(self, limit):
        """
        Ensures the user provides a valid integer within the specified range (1 to limit).
        This function prevents the program from crashing if the user enters letters or symbols.
        """
        while True:
            try:
                # Get input and remove extra spaces
                user_input = input(f"\nSelect a number (1-{limit}): ").strip()
                
                # Try converting input to an integer
                choice = int(user_input)
                
                # Check if the number is within the available options
                if 1 <= choice <= limit:
                    # Return (choice - 1) to match Python's 0-based indexing for lists
                    return choice - 1
                
                # If number is out of range
                print(f"⚠️ Out of range! Please choose between 1 and {limit}.")
                
            except ValueError:
                # This block runs if the user enters something that isn't a number (like 'abc')
                print("⚠️ Invalid input! Please enter a numeric value.")

    def run_user_experience(self, all_cities):
        """
        The main engine of the user journey. 
        Provides two entry points: Guided Discovery or Direct Access.
        """
        self.clear_screen()
        self.show_header("Saudi Adventure Planner")

        # --- FEATURE: CHOOSE ENTRY PATH ---
        print("\nHow would you like to start?")
        print("1- Explore & Discover: Find a city based on your preferred vibe.")
        print("2- Direct Access: I already know my destination.")
        
        path_choice = self.get_number_choice(2)

        if path_choice == 0:
            # Path 1: The original filtering flow (Discovery)
            self.guided_discovery_flow(all_cities)
        else:
            # Path 2: Direct selection flow (Shortcut)
            self.direct_city_flow(all_cities)

    def guided_discovery_flow(self, all_cities):
        """
        Path 1: Filtering cities based on terrain (Guided Discovery).
        Now displays City Name and Short Description.
        """
        self.clear_screen()
        self.show_header("Guided Discovery")

        while True:
            # Inform the user about their options
            print("\n🌍 What's your vibe? (Coastal, Mountain, Desert, Urban)")
            terrain_choice = input("Enter preference or hit Enter to EXPLORE ALL: ").strip().lower()
            
            # --- INTELLIGENT FILTERING LOGIC ---
            suitable = [
                city for city in all_cities 
                if any(terrain_choice in t.lower() for t in city.get('terrain', []))
            ]
            
            # If no matches found, we default to showing all cities (Fall-back mechanism)
            final_list = suitable if (suitable and terrain_choice != "") else all_cities
            
            if not suitable and terrain_choice != "": 
                print(f"\n⚠️ No exact matches for '{terrain_choice}'. Showing all gems!")

            # --- DISPLAYING THE FILTERED LIST ---
            print("\nRecommended Destinations:")
            for idx, city in enumerate(final_list, 1):
                # Modification: Displaying Name and Short Description instead of just terrain
                short_desc = city.get('short_description', 'No description available.')
                print(f"{idx} - {city['name']} | {short_desc}")
            
            # Get the index of the chosen city
            city_idx = self.get_number_choice(len(final_list))
            selected_city = final_list[city_idx]
            
            # Confirmation step
            if self.confirm_selection(selected_city):
                break

        self.process_activity_selection(selected_city)

    def direct_city_flow(self, all_cities):
        """
        Path 2: Showing all cities immediately for direct selection.
        Displays City Name and Short Description.
        """
        self.clear_screen()
        self.show_header("Direct City Access")
        
        print("\nWhich city do you want to explore?")
        for idx, city in enumerate(all_cities, 1):
            # Modification: Displaying Name and Short Description
            short_desc = city.get('short_description', 'No description available.')
            print(f"{idx} - {city['name']} | {short_desc}")
            
        city_idx = self.get_number_choice(len(all_cities))
        selected_city = all_cities[city_idx]
        
        if self.confirm_selection(selected_city):
            self.process_activity_selection(selected_city)
        else:
            self.run_user_experience(all_cities) # Back to start if not confirmed

    def confirm_selection(self, city):
        """
        Helper to show city details and get confirmation.
        Modified order: Best time to visit is shown before the full description.
        """
        self.clear_screen()
        self.show_header(f"Destination: {city['name']}")

        # 1. Show Best Time to Visit FIRST
        best_time = city.get('best_time_to_visit', 'All year round')
        print(f"📅 BEST TIME TO VISIT: {best_time}")
        print("-" * 30)

        # 2. Show the Full Description
        full_desc = city.get('full_description', 'Explore this amazing city!')
        print(f"📖 ABOUT THE CITY:\n{full_desc}")
        
        print("-" * 60)
        confirm = input("\nDo you want to select this city? (yes/no): ").strip().lower()
        return confirm in ["yes", "y"]

    def process_activity_selection(self, city):
        """
        Dynamically extracts activity categories from the city's JSON data.
        """
        # Get the keys from activities_data (like 'historical_sites', 'shopping')
        categories = list(city.get("activities_data", {}).keys())
        
        if not categories:
            print("⚠️ No activities listed for this city yet.")
            return

        print(f"\nWhat would you like to do in {city['name']}?")
        # Display categories with clean formatting
        for i, cat in enumerate(categories, 1):
            print(f"{i}- {cat.replace('_', ' ').title()}")
        
        cat_idx = self.get_number_choice(len(categories))
        activity_type = categories[cat_idx]

        # Pass the specific activity list to the final display function
        self.display_itinerary(
            city['name'], 
            city['activities_data'].get(activity_type, []), 
            city.get('travel_tips', [])
        )

    def display_itinerary(self, city_name, plan, tips):
        """
        Formats and prints the final travel plan.
        """
        self.show_header(f"Your Itinerary for {city_name}")
        
        if not plan:
            print("📍 No specific activities found in this category.")
        else:
            for act in plan:
                print(f"📍 [{act.get('best_time', 'Anytime')}] - {act['name']}")
                
                # Only show Cafe/Restaurant if they exist in JSON
                if act.get('nearby_cafe'): 
                    print(f"   ☕ Cafe: {act['nearby_cafe']}")
                if act.get('nearby_restaurant'): 
                    print(f"   🍴 Dining: {act['nearby_restaurant']}")
                print("-" * 40)
        
        if tips:
            print("\n💡 TRAVEL TIPS:")
            for tip in tips: 
                print(f" • {tip}")
                
        print("\n" + "="*60)
        # Pause the program so the user can read the results before clearing the screen
        input("\nPress Enter to return to main menu...")