import os
import json
import textwrap
from textblob import TextBlob # We use TextBlob for NLP and Sentiment Analysis

class UserInterface:
    def __init__(self):
        # We ensure the recommendations folder exists at startup to prevent 
        # 'File Not Found' errors during runtime.
        self.reviews_folder = 'recommendations'
        if not os.path.exists(self.reviews_folder):
            os.makedirs(self.reviews_folder)

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

    # --- NEW: NLP & Sentiment Analysis Logic ---
    def process_smart_comment(self, raw_comment):
        """
        Integrating NLP here allows us to 'Clean' user input and automatically 
        detect the mood (Sentiment) of the review to help future travelers.
        """
        blob = TextBlob(raw_comment)
        # We use the Polarity score (-1.0 to 1.0) to categorize user experience.
        score = blob.sentiment.polarity
        
        if score > 0.1:
            sentiment = "Positive 😊"
        elif score < -0.1:
            sentiment = "Negative ☹️"
        else:
            sentiment = "Neutral 😐"
            
        return str(blob.correct()), sentiment

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
            
            # Here, the confirmation page makes sense because the user is exploring options.
            if self.confirm_selection(selected_city):
                break
        
        self.show_post_selection_menu(selected_city)

    def direct_city_flow(self, all_cities):
        self.clear_screen()
        self.show_header("Direct City Access")
        print("\nWhich city do you want to explore?")
        for idx, city in enumerate(all_cities, 1):
            city_name = city.get('name', 'Unknown City')
            print(f"{idx} - {city_name}")
            
        city_idx = self.get_number_choice(len(all_cities))
        selected_city = all_cities[city_idx]
        
        # --- FIXED UX: FAST PATH ---
        # We skip the confirmation/description screen here. Since the user chose 
        # 'Direct Access', they don't need to re-read the city bio.
        self.show_post_selection_menu(selected_city)

    def confirm_selection(self, city):
        self.clear_screen()
        city_name = city.get('name', 'this destination')
        self.show_header(f"Destination: {city_name}")

        rating = city.get('average_rating', 'N/A')
        print(f"⭐ RATING: {rating}/5  |  🌤️ CLIMATE: {city.get('climate', 'N/A')}")
        print(f"📅 BEST TIME TO VISIT: {city.get('best_time_to_visit', 'All year round')}")
        print("-" * 65)
        print(f"📖 ABOUT THE CITY:\n{city.get('full_description', 'Explore this amazing city!')}")
        print("-" * 65)
        confirm = input("\nDo you want to select this city? (yes/no): ").strip().lower()
        return confirm in ["yes", "y"]

    # --- NEW: Menu for Reviews & Planning ---
    def show_post_selection_menu(self, city):
        """
        By splitting planning and community reviews, we separate 'Facts' (Itineraries) 
        from 'Opinions' (Reviews) to give the user a balanced perspective.
        """
        while True:
            self.clear_screen()
            self.show_header(f"Explore {city.get('name')}")
            print("1- View Planned Itineraries (Expert Guides)")
            print("2- Community Reviews (What others are saying)")
            print("3- Add Your Own Review (Share your experience)")
            print("4- Back to Main Menu")
            
            choice = self.get_number_choice(4)
            
            if choice == 0:
                self.process_activity_selection(city)
            elif choice == 1:
                self.view_community_reviews(city.get('id', 'aseer'))
            elif choice == 2:
                self.add_new_recommendation(city)
            else:
                break

    def view_community_reviews(self, city_id):
        # We use a modular path approach to ensure the correct JSON file 
        # is loaded based on the current city ID.
        path = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")
        
        if not os.path.exists(path):
            print("\n📍 No reviews found for this city yet. Be the first to add one!")
            input("Press Enter to return...")
            return

        with open(path, 'r', encoding='utf-8') as f:
            reviews = json.load(f)

        self.clear_screen()
        self.show_header(f"Community Insights: {city_id.title()}")
        
        for r in reviews:
            # We display the Sentiment label alongside the review to provide 
            # instant visual feedback on the quality of the feedback.
            print(f"👤 {r['user']} ({r['nationality']}) - {r['type']}")
            print(f"   Vibe: {r.get('sentiment', 'N/A')}")
            print(f"   💬 \"{r['comment']}\"")
            print("-" * 35)
        
        input("\nPress Enter to continue...")

    def add_new_recommendation(self, city):
        self.clear_screen()
        city_id = city.get('id', 'aseer')
        city_name = city.get('name', 'City')
        self.show_header(f"Add Your Review for {city_name}")

        print("📝 Please share your feedback (English only):")
        raw_text = input(">> ").strip()
        
        # We process the text using NLP to detect sentiment before saving.
        print("\n✨ Polishing and analyzing your feedback...")
        polished, mood = self.process_smart_comment(raw_text)

        name = input("👤 Your Name: ").strip() or "Guest"
        nat = input("🏳️ Your Nationality: ").strip() or "International"
        is_saudi = input("🇸🇦 Are you a Saudi Local? (y/n): ").lower() == 'y'

        new_entry = {
            "city": city_name,
            "user": name,
            "nationality": nat,
            "type": "Local" if is_saudi else "Tourist",
            "comment": polished,
            "sentiment": mood
        }

        # Saving to a separate folder ensures our core data and user feedback 
        # remain decoupled for better database management.
        path = os.path.join(self.reviews_folder, f"{city_id}_reviews.json")
        reviews = []
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                reviews = json.load(f)
        
        reviews.append(new_entry)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, indent=4, ensure_ascii=False)

        print("\n✅ Your review has been saved! Thank you for contributing.")
        input("Press Enter to continue...")

    def process_activity_selection(self, city):
        activities_data = city.get("activities_data", {})
        categories = list(activities_data.keys())
        
        if not categories:
            print("⚠️ No activities listed for this city yet.")
            input("Press Enter to continue...") # Small UX fix to see the message
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
        self.clear_screen()
        self.show_header(f"Detailed Itinerary: {city_name}")
        
        if not plan:
            print("📍 No specific activities found in this category.")
        else:
            for act in plan:
                print(f"📍 {act.get('name', 'Unknown Activity').upper()}")
                print(f"   ✨ Vibe: {act.get('vibe', 'N/A')}  |  💰 Budget: {act.get('budget', 'N/A')}")
                print(f"   🕒 Best Time: {act.get('best_time', 'Anytime')}")
                # We use textwrap to ensure comments look clean in the console.
                comment = act.get('experience_summary', 'No summary available.')
                print(f"   📝 Experience: {textwrap.fill(comment, width=60)}")
                
                cafe = act.get('nearby_cafe')
                rest = act.get('nearby_restaurant')
                dish = act.get('signature_dish')
                
                if cafe or rest:
                    print(f"   🍽️  Where to go:")
                    if cafe: print(f"      ☕ Cafe: {cafe}")
                    if rest: print(f"      🍴 Dining: {rest}")
                    if dish: print(f"      🥘 MUST TRY: {dish}")
                
                tip = act.get('local_tip')
                if tip:
                    print(f"   💡 Local Tip: {tip}")
                
                print("-" * 65)
        
        if tips:
            print("\n💡 GENERAL TRAVEL TIPS:")
            for tip in tips:
                print(f" • {tip}")
        
        input("\nPress Enter to return...")