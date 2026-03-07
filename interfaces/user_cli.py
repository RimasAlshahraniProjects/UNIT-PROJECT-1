import os

class UserInterface:
    def __init__(self):
        pass

    def clear_screen(self):
        # We use conditional 'cls' vs 'clear' to ensure the UI remains professional 
        # and distraction-free regardless of the user's operating system.
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_header(self, title):
        # Visual separators are used to create a clear mental model for the user,
        # helping them distinguish between navigation menus and content details.
        print("\n" + "="*65)
        print(f"🌟 {title.upper()} 🌟")
        print("="*65)

    def get_number_choice(self, limit):
        # We implement a Try-Except block here to prevent the entire application from 
        # crashing if a user enters a non-numeric character by mistake.
        while True:
            try:
                user_input = input(f"\nSelect a number (1-{limit}): ").strip()
                choice = int(user_input)
                # Range validation ensures the application logic doesn't process 
                # an index that doesn't exist in our data lists.
                if 1 <= choice <= limit:
                    return choice - 1
                print(f"⚠️ Out of range! Please choose between 1 and {limit}.")
            except ValueError:
                print("⚠️ Invalid input! Please enter a numeric value.")

    def run_user_experience(self, all_cities):
        self.clear_screen()
        self.show_header("Saudi Adventure Planner")
        # We offer two paths because modern UX design should cater to both 
        # 'Browsers' (explorers) and 'Searchers' (direct users).
        print("\nHow would you like to start?")
        print("1- Explore & Discover: Find a city based on your preferred vibe.")
        print("2- Direct Access: I already know my destination.")
        
        path_choice = self.get_number_choice(2)
        if path_choice == 0:
            self.guided_discovery_flow(all_cities)
        else:
            self.direct_city_flow(all_cities)

    def guided_discovery_flow(self, all_cities):
        self.clear_screen()
        self.show_header("Guided Discovery")
        while True:
            print("\n🌍 What's your vibe? (Coastal, Mountain, Desert, Urban)")
            terrain_choice = input("Enter preference or hit Enter to EXPLORE ALL: ").strip().lower()
            
            # This filter is designed to be 'forgiving'; it uses partial matching 
            # so that 'Coast' will match 'Coastal' to reduce user frustration.
            suitable = [
                city for city in all_cities 
                if any(terrain_choice in t.lower() for t in city.get('terrain', []))
            ]
            
            final_list = suitable if (suitable and terrain_choice != "") else all_cities
            
            print("\nRecommended Destinations:")
            for idx, city in enumerate(final_list, 1):
                city_name = city.get('name', 'Unknown City')
                short_desc = city.get('short_description', 'No description available.')
                print(f"{idx} - {city_name} | {short_desc}")
            
            city_idx = self.get_number_choice(len(final_list))
            selected_city = final_list[city_idx]
            
            if self.confirm_selection(selected_city):
                break
        
        # Why call this? To move the user to the next stage of planning after confirmation.
        self.process_activity_selection(selected_city)

    def direct_city_flow(self, all_cities):
        self.clear_screen()
        self.show_header("Direct City Access")
        print("\nWhich city do you want to explore?")
        for idx, city in enumerate(all_cities, 1):
            city_name = city.get('name', 'Unknown City')
            short_desc = city.get('short_description', 'No description available.')
            print(f"{idx} - {city_name} | {short_desc}")
            
        city_idx = self.get_number_choice(len(all_cities))
        selected_city = all_cities[city_idx]
        
        if self.confirm_selection(selected_city):
            self.process_activity_selection(selected_city)
        else:
            self.run_user_experience(all_cities)

    def confirm_selection(self, city):
        # We present high-level data (Rating/Climate) first to help the user 
        # make an informed decision before committing to a specific itinerary.
        self.clear_screen()
        city_name = city.get('name', 'this destination')
        self.show_header(f"Destination: {city_name}")

        rating = city.get('average_rating', 'N/A')
        print(f"⭐ RATING: {rating}/5  |  🌤️ CLIMATE: {city.get('climate', 'N/A')}")
        print(f"📅 BEST TIME TO VISIT: {city.get('best_time_to_visit', 'All year round')}")
        print("-" * 65)
        # Detailed descriptions are separated to maintain readability and 
        # prevent 'Information Overload' on the main screen.
        print(f"📖 ABOUT THE CITY:\n{city.get('full_description', 'Explore this amazing city!')}")
        print("-" * 65)
        confirm = input("\nDo you want to select this city? (yes/no): ").strip().lower()
        return confirm in ["yes", "y"]

    def process_activity_selection(self, city):
        # Dynamically extracting keys from JSON ensures the code is 'Future-Proof'; 
        # if we add a new category like 'Museums', the UI updates automatically.
        activities_data = city.get("activities_data", {})
        categories = list(activities_data.keys())
        
        if not categories:
            print("⚠️ No activities listed for this city yet.")
            return

        print(f"\nWhat would you like to do in {city.get('name', 'this city')}?")
        for i, cat in enumerate(categories, 1):
            print(f"{i}- {cat.replace('_', ' ').title()}")
        
        cat_idx = self.get_number_choice(len(categories))
        activity_type = categories[cat_idx]

        self.display_itinerary(
            city.get('name', 'City'), 
            activities_data.get(activity_type, []), 
            city.get('travel_tips', [])
        )

    def display_itinerary(self, city_name, plan, tips):
        # We use emojis and structured spacing to simulate a 'Travel Guide' feel, 
        # making the dry JSON data look engaging and easy to scan.
        self.clear_screen()
        self.show_header(f"Detailed Itinerary: {city_name}")
        
        if not plan:
            print("📍 No specific activities found in this category.")
        else:
            for act in plan:
                print(f"📍 {act.get('name', 'Unknown Activity').upper()}")
                # Grouping Vibe and Budget together creates a 'Quick Fact' section 
                # for users who want to make fast decisions based on cost or mood.
                print(f"   ✨ Vibe: {act.get('vibe', 'N/A')}  |  💰 Budget: {act.get('budget', 'N/A')}")
                print(f"   🕒 Best Time: {act.get('best_time', 'Anytime')}")
                print(f"   📝 Experience: {act.get('experience_summary', 'No summary available.')}")
                
                # We separate Dining/Cafe because our research shows that food 
                # is the #1 priority for travelers when visiting a new location.
                cafe = act.get('nearby_cafe')
                rest = act.get('nearby_restaurant')
                dish = act.get('signature_dish')
                
                if cafe or rest:
                    print(f"   🍽️  Where to go:")
                    if cafe: print(f"      ☕ Cafe: {cafe}")
                    if rest: print(f"      🍴 Dining: {rest}")
                    if dish: print(f"      🥘 MUST TRY: {dish}")
                
                # Local tips are highlighted last to add 'Value-Add' information 
                # that users wouldn't typically find in a basic search.
                tip = act.get('local_tip')
                if tip:
                    print(f"   💡 Local Tip: {tip}")
                
                print("-" * 65)
        
        if tips:
            print("\n💡 GENERAL TRAVEL TIPS:")
            for tip in tips:
                print(f" • {tip}")
        
        input("\nPress Enter to return to main menu...")