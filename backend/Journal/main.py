# backend/journal/main.py
# Terminal interface for testing Eco-Journal functionality

import os
import sys

# Add project paths
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  #for config.py of journal
sys.path.append(os.path.join(os.path.dirname(__file__), '../../Database'))
sys.path.append(os.path.dirname(__file__))


from datetime import datetime, date
from typing import Dict, Any
import json



# Import our services
from backend.Journal.journal_service import EcoJournalService
from backend.Journal.config import Config
from Database.Journal import DatabaseManager

db_manager = DatabaseManager()

class EcoJournalCLI:
    """Command-line interface for Eco-Journal testing"""
    
    def __init__(self):
        print("🌱 Initializing Eco-Journal System...")
        try:
            self.service = EcoJournalService()
            self.user_id = Config.DEFAULT_USER_ID
            print(f"✅ System ready! Using user ID: {self.user_id}")
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            print("Please check your database connections and dependencies.")
            sys.exit(1)
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*60)
        print("🌍 ECO-JOURNAL SYSTEM")
        print("="*60)
        print("1. 📝 Create Journal Entry")
        print("2. 🔥 View Streak Status")
        print("3. 📊 View Dashboard")
        print("4. 🎯 Use Streak Freeze")
        print("5. 💭 Get Mood-based Inspiration")
        print("6. 📈 View Analytics")
        print("7. 🏆 View Achievements")
        print("8. 🔧 System Test")
        print("0. ❌ Exit")
        print("="*60)
    
    def run(self):
        """Main CLI loop"""
        print("🌱 Welcome to the Eco-Journal System!")
        print("This system analyzes your eco-habits and provides motivational insights.")
        
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (0-8): ").strip()
            
            try:
                if choice == "1":
                    self.create_journal_entry()
                elif choice == "2":
                    self.view_streak_status()
                elif choice == "3":
                    self.view_dashboard()
                elif choice == "4":
                    self.use_streak_freeze()
                elif choice == "5":
                    self.get_mood_inspiration()
                elif choice == "6":
                    self.view_analytics()
                elif choice == "7":
                    self.view_achievements()
                elif choice == "8":
                    self.system_test()
                elif choice == "0":
                    print("👋 Thank you for using Eco-Journal! Keep saving the planet! 🌍")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                input("Press Enter to continue...")
    
    def create_journal_entry(self):
        """Create a new journal entry"""
        print("\n📝 CREATE JOURNAL ENTRY")
        print("-" * 40)
        print("Write about your eco-habits, feelings, or environmental actions today.")
        print("Examples:")
        print("• I used my bicycle instead of the car today and felt great!")
        print("• I'm feeling guilty about forgetting to recycle yesterday.")
        print("• Started composting today - excited to reduce food waste!")
        print()
        
        content = input("Your journal entry: ").strip()
        
        if not content:
            print("❌ Cannot create empty journal entry.")
            return
        
        print("\n🧠 Processing your entry...")
        
        # Process the journal entry
        result = self.service.process_journal_entry(self.user_id, content)
        
        if result.get('success'):
            self.display_journal_result(result)
        else:
            print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
        
        input("\nPress Enter to continue...")
    
    def display_journal_result(self, result: Dict[str, Any]):
        """Display the results of journal processing"""
        print("\n" + "="*60)
        print("✅ JOURNAL ENTRY PROCESSED!")
        print("="*60)
        
        # Sentiment Analysis
        analysis = result['analysis']
        sentiment = analysis['sentiment']
        print(f"📊 SENTIMENT: {sentiment['label']} (confidence: {sentiment['confidence']:.2f})")
        
        # Emotions
        print(f"😊 EMOTION SUMMARY: {analysis['emotion_summary']}")
        
        if analysis['eco_tags']:
            print(f"🏷️  ECO CATEGORIES: {', '.join(analysis['eco_tags'])}")
        
        # Inspiration
        print(f"\n💡 INSPIRATION:")
        print(f"   {result['inspiration']}")
        
        # Streak Information
        streak = result['streak']
        print(f"\n🔥 STREAK UPDATE:")
        print(f"   Current Streak: {streak['current_streak']} days")
        print(f"   Longest Streak: {streak['longest_streak']} days")
        print(f"   Total Entries: {streak['total_entries']}")
        print(f"   Event: {streak['streak_event']}")
        
        # New Achievements
        if streak['new_achievements']:
            print(f"\n🏆 NEW ACHIEVEMENTS:")
            for achievement in streak['new_achievements']:
                print(f"   {achievement['badge']} {achievement['name']}: {achievement['description']}")
        
        # Next Milestone
        if streak['next_milestone']:
            milestone = streak['next_milestone']
            print(f"\n🎯 NEXT MILESTONE:")
            print(f"   {milestone['badge']} {milestone['name']}: {milestone['days_remaining']} days to go!")
            print(f"   Progress: {milestone['progress_percentage']}%")
    
    def view_streak_status(self):
        """View current streak status"""
        print("\n🔥 STREAK STATUS")
        print("-" * 40)
        
        status = self.service.streak_manager.get_streak_status(self.user_id)
        
        if status.get('error'):
            print(f"❌ Error: {status['message']}")
            return
        
        print(f"Current Streak: {status['current_streak']} days")
        print(f"Longest Streak: {status['longest_streak']} days")
        print(f"Total Entries: {status['total_entries']}")
        
        if status['last_entry_date']:
            print(f"Last Entry: {status['last_entry_date']}")
            print(f"Days Since Last Entry: {status['days_since_last_entry']}")
        
        if status['streak_at_risk']:
            print("⚠️  WARNING: Your streak is at risk! Make an entry today.")
        
        print(f"\nStreak Frozen: {'Yes' if status['streak_frozen'] else 'No'}")
        print(f"Freeze Count: {status['freeze_count']}")
        print(f"Freezes Remaining: {status['freezes_remaining']}")
        
        if status['next_milestone']:
            milestone = status['next_milestone']
            print(f"\nNext Milestone: {milestone['badge']} {milestone['name']}")
            print(f"Progress: {milestone['progress_percentage']}% ({milestone['days_remaining']} days to go)")
        
        input("\nPress Enter to continue...")
    
    def view_dashboard(self):
        """View user dashboard"""
        print("\n📊 USER DASHBOARD")
        print("-" * 40)
        
        dashboard = self.service.get_user_dashboard(self.user_id)
        
        if 'error' in dashboard:
            print(f"❌ Error: {dashboard['error']}")
            return
        
        # Streak Status Summary
        streak = dashboard['streak_status']
        print(f"🔥 Current Streak: {streak['current_streak']} days")
        print(f"🏆 Longest Streak: {streak['longest_streak']} days")
        print(f"📝 Total Entries: {streak['total_entries']}")
        
        # Recent Entries Summary
        recent = dashboard['recent_entries']
        print(f"\n📖 Recent Activity:")
        print(f"   Total Entries: {recent['count']}")
        
        if recent['summary']['total_entries'] > 0:
            summary = recent['summary']
            print(f"   Dominant Sentiment: {summary['dominant_sentiment']}")
            if summary['common_eco_tags']:
                print(f"   Common Eco-Tags: {', '.join(summary['common_eco_tags'])}")
        
        # Analytics
        analytics = dashboard['analytics']
        print(f"\n📈 30-Day Analytics:")
        print(f"   Consistency Rate: {analytics['consistency_rate']}%")
        print(f"   Total Events: {analytics['total_events']}")
        
        # Achievements
        if streak['achievements']:
            print(f"\n🏆 Achievements ({len(streak['achievements'])}):")
            for achievement in streak['achievements'][:3]:  # Show top 3
                print(f"   {achievement['badge']} {achievement['name']}")
        
        # Recommendations
        if dashboard['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in dashboard['recommendations']:
                print(f"   • {rec}")
        
        input("\nPress Enter to continue...")
    
    def use_streak_freeze(self):
        """Use a streak freeze"""
        print("\n❄️  USE STREAK FREEZE")
        print("-" * 40)
        print("Streak freezes protect your streak if you miss a day.")
        
        confirm = input("Are you sure you want to use a freeze? (y/n): ").lower().strip()
        if confirm != 'y':
            print("Cancelled.")
            return
        
        result = self.service.streak_manager.use_streak_freeze(self.user_id)
        
        if result['success']:
            print("✅ Streak freeze activated!")
            print(f"Current Streak: {result['current_streak']} days (Protected)")
            print(f"Freezes Remaining: {result['freezes_remaining']}")
        else:
            print(f"❌ {result['message']}")
        
        input("\nPress Enter to continue...")
    
    def get_mood_inspiration(self):
        """Get inspiration based on mood"""
        print("\n💭 MOOD-BASED INSPIRATION")
        print("-" * 40)
        print("How are you feeling today?")
        print("1. Happy 😊")
        print("2. Sad 😢")
        print("3. Frustrated 😤")
        print("4. Motivated 💪")
        print("5. Guilty 😔")
        print("6. Neutral 😐")
        
        mood_map = {
            "1": "happy", "2": "sad", "3": "frustrated",
            "4": "motivated", "5": "guilty", "6": "neutral"
        }
        
        choice = input("\nSelect your mood (1-6): ").strip()
        
        if choice not in mood_map:
            print("❌ Invalid choice.")
            return
        
        mood = mood_map[choice]
        result = self.service.get_inspiration_for_mood(self.user_id, mood)
        
        if 'error' not in result:
            print(f"\n💡 Inspiration for {mood.title()} mood:")
            print(f"   {result['inspiration']}")
            
            print(f"\n✨ Suggestions:")
            for suggestion in result['suggestions']:
                print(f"   • {suggestion}")
        else:
            print(f"❌ Error: {result['error']}")
        
        input("\nPress Enter to continue...")
    
    def view_analytics(self):
        """View detailed analytics"""
        print("\n📈 DETAILED ANALYTICS")
        print("-" * 40)
        
        analytics = self.service.streak_manager.get_streak_analytics(self.user_id, days=30)
        
        if 'error' in analytics:
            print(f"❌ Error: {analytics['error']}")
            return
        
        print(f"📊 30-Day Analysis:")
        print(f"   Total Events: {analytics['total_events']}")
        print(f"   Consistency Rate: {analytics['consistency_rate']}%")
        print(f"   Average Streak Length: {analytics['average_streak_length']:.1f} days")
        print(f"   Longest Streak in Period: {analytics['longest_streak_in_period']} days")
        
        if analytics['event_breakdown']:
            print(f"\n📋 Event Breakdown:")
            for event_type, count in analytics['event_breakdown'].items():
                print(f"   {event_type.title()}: {count}")
        
        input("\nPress Enter to continue...")
    
    def view_achievements(self):
        """View all achievements"""
        print("\n🏆 ACHIEVEMENTS")
        print("-" * 40)
        
        status = self.service.streak_manager.get_streak_status(self.user_id)
        achievements = status.get('achievements', [])
        
        if not achievements:
            print("No achievements yet. Keep journaling to earn your first badge! 🌱")
        else:
            print(f"You have earned {len(achievements)} achievement(s):")
            for achievement in achievements:
                earned_date = datetime.fromisoformat(achievement['earned_at']).strftime('%Y-%m-%d')
                print(f"\n{achievement['badge']} {achievement['name']}")
                print(f"   {achievement['description']}")
                print(f"   Earned: {earned_date} (Streak: {achievement['streak_when_earned']} days)")
        
        input("\nPress Enter to continue...")
    
    def system_test(self):
        """Run system tests"""
        print("\n🔧 SYSTEM TEST")
        print("-" * 40)
        
        test_entries = [
            "I rode my bicycle to work today and felt amazing! The fresh air was so refreshing.",
            "I'm feeling guilty about using plastic bags at the grocery store today.",
            "Started a small herb garden on my balcony - excited about growing my own food!",
            "Frustrated with how much plastic packaging comes with online orders.",
            "Successfully composted for a full week now. Proud of reducing my food waste!"
        ]
        
        print("Running tests with sample journal entries...\n")
        
        for i, entry in enumerate(test_entries, 1):
            print(f"Test {i}/5: Processing sample entry...")
            result = self.service.process_journal_entry(self.user_id, entry)
            
            if result.get('success'):
                sentiment = result['analysis']['sentiment']['label']
                streak = result['streak']['current_streak']
                print(f"✅ Success - Sentiment: {sentiment}, Streak: {streak}")
            else:
                print(f"❌ Failed - {result.get('error')}")
        
        print(f"\n🎯 System test completed!")
        input("Press Enter to continue...")

def main():
    """Main entry point"""
    try:
        cli = EcoJournalCLI()
        cli.run()
    except Exception as e:
        print(f"❌ Critical error: {e}")
        print("Please check your configuration and database connections.")

if __name__ == "__main__":
    main()