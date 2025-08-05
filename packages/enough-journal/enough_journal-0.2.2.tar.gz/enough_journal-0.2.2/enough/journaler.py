#!/usr/bin/env python3
"""
ENOUGH - Nathaniel Branden Sentence Completion Journal
"""

import yaml
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class ProgressTracker:
    def __init__(self):
        self.progress_file = Path("progress.json")
        self.load_progress()
    
    def is_first_run(self) -> bool:
        """Check if this is the first time running the program"""
        return not self.progress_file.exists()
    
    def initialize_new_user(self):
        """Initialize progress for a new user"""
        print("\nWelcome to ENOUGH - Nathaniel Branden Sentence Completion")
        print("=" * 60)
        print("This is your first time running the program.")
        print("\nWould you like to:")
        print("1. Start fresh (begin at Week 1, Day 1)")
        print("2. Continue existing practice (set current week/day)")
        
        while True:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            
            if choice == "1":
                self.progress = {
                    "current_week": 1,
                    "current_stem_index": 0,
                    "start_date": date.today().isoformat(),
                    "completed_stems": [],
                    "daily_entries": {},
                    "is_new_user": True
                }
                print("Starting fresh at Week 1, Day 1")
                break
                
            elif choice == "2":
                self.setup_existing_user()
                break
                
            else:
                print("Please enter 1 or 2")
        
        self.save_progress()
    
    def setup_existing_user(self):
        """Setup progress for user continuing existing practice"""
        print("\nContinuing Existing Practice")
        print("=" * 40)
        
        # Get current week
        while True:
            try:
                week = int(input("What week are you currently on? (1-30): "))
                if 1 <= week <= 30:
                    break
                else:
                    print("Week must be between 1 and 30")
            except ValueError:
                print("Please enter a number")
        
        # Calculate start date (assuming 7 days per week)
        days_elapsed = (week - 1) * 7
        start_date = date.today() - timedelta(days=days_elapsed)
        
        # Determine current stem based on day of week
        current_weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday
        if current_weekday >= 5:  # Weekend
            stem_index = 0  # Start with first stem of the week
        else:
            stem_index = current_weekday  # Monday=0, Tuesday=1, etc.
        
        self.progress = {
            "current_week": week,
            "current_stem_index": stem_index,
            "start_date": start_date.isoformat(),
            "completed_stems": [],
            "daily_entries": {},
            "is_new_user": False
        }
        
        print(f"Set up for Week {week}")
        print(f"Calculated start date: {start_date.strftime('%Y-%m-%d')}")
        print(f"Today's stem: {stem_index + 1} (based on current day)")
    
    def calculate_progress_from_start_date(self):
        """Calculate current week and stem based on start date"""
        if "start_date" not in self.progress:
            return
        
        start_date = date.fromisoformat(self.progress["start_date"])
        today = date.today()
        days_elapsed = (today - start_date).days
        
        # Calculate week and stem
        weeks_elapsed = days_elapsed // 7
        days_in_current_week = days_elapsed % 7
        
        current_week = weeks_elapsed + 1
        current_stem = days_in_current_week + 1
        
        # Update progress if calculated values differ
        if (self.progress.get("current_week", 1) != current_week or 
            self.progress.get("current_stem_index", 0) != current_stem - 1):
            
            print(f"\n📊 Progress Update:")
            print(f"   Start Date: {start_date.strftime('%Y-%m-%d')}")
            print(f"   Days Elapsed: {days_elapsed}")
            print(f"   Current Week: {current_week}")
            print(f"   Current Day: {current_stem}")
            
            self.progress["current_week"] = current_week
            self.progress["current_stem_index"] = current_stem - 1
            self.save_progress()
    
    def load_progress(self):
        """Load current progress from file"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
            
            # Calculate progress from start date for returning users
            if not self.progress.get("is_new_user", False):
                self.calculate_progress_from_start_date()
        else:
            # First time running - will be initialized in main()
            self.progress = {}
    
    def save_progress(self):
        """Save current progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def get_current_stem(self, exercises: List[Dict]) -> Optional[Dict]:
        """Get the current sentence stem for this week"""
        current_week = self.progress["current_week"]
        week_exercises = [ex for ex in exercises if ex.get("week") == current_week and ex.get("type") == "sentence_completion"]
        
        if not week_exercises:
            return None
        
        stem_index = self.progress.get("current_stem_index", 0)
        if stem_index >= len(week_exercises):
            return None
        
        return week_exercises[stem_index]
    
    def get_week_stems(self, exercises: List[Dict]) -> List[Dict]:
        """Get all sentence stems for the current week"""
        current_week = self.progress["current_week"]
        week_exercises = [ex for ex in exercises if ex.get("week") == current_week and ex.get("type") == "sentence_completion"]
        return week_exercises
    
    def advance_stem(self):
        """Move to next stem in current week"""
        self.progress["current_stem_index"] += 1
        self.save_progress()
    
    def advance_day(self):
        """Track that we completed today's practice"""
        # Mark today as completed
        today = date.today().isoformat()
        if "completed_days" not in self.progress:
            self.progress["completed_days"] = []
        
        if today not in self.progress["completed_days"]:
            self.progress["completed_days"].append(today)
        
        self.save_progress()
    
    def advance_week(self):
        """Move to next week after weekend reflection"""
        self.progress["current_week"] += 1
        self.progress["completed_days"] = []  # Reset for new week
        self.save_progress()
    
    def is_week_complete(self) -> bool:
        """Check if we've completed all days of the current week"""
        if "completed_days" not in self.progress:
            return False
        
        # Count how many weekdays we've completed this week
        current_week = self.progress["current_week"]
        weekdays_completed = len([day for day in self.progress["completed_days"] 
                                if date.fromisoformat(day).isocalendar()[1] == date.today().isocalendar()[1]])
        
        # Consider week complete after 5 weekdays or if it's weekend
        return weekdays_completed >= 5 or self.is_weekend()
    
    def is_weekend(self) -> bool:
        """Check if today is weekend (Saturday or Sunday)"""
        return datetime.now().weekday() >= 5
    
    def get_weekend_reflection(self, exercises: List[Dict]) -> Optional[Dict]:
        """Get weekend reflection exercise"""
        for exercise in exercises:
            if exercise.get("type") == "weekend_reflection":
                return exercise
        return None

class Journaler:
    def __init__(self):
        self.tracker = ProgressTracker()
        self.journals_dir = Path("journals")
        self.journals_dir.mkdir(exist_ok=True)
    
    def load_exercises(self) -> List[Dict]:
        """Load exercises from exercises.yaml"""
        import os
        import sys
        
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try multiple locations for exercises.yaml
        possible_paths = [
            "exercises.yaml",  # Current directory
            os.path.join(package_dir, "exercises.yaml"),  # Package directory
            os.path.join(os.path.dirname(package_dir), "exercises.yaml"),  # Parent directory
        ]
        
        for path in possible_paths:
            try:
                with open(path) as f:
                    data = yaml.safe_load(f)
                    return data.get("exercises", [])
            except FileNotFoundError:
                continue
        
        print("exercises.yaml not found!")
        return []
    
    def save_daily_entry(self, stem: Dict, completions: List[str]):
        """Save daily sentence completions"""
        today = datetime.now()
        stem_id = stem.get("stem_id", "unknown")
        
        entry = {
            "date": today.strftime('%Y-%m-%d'),
            "time": today.strftime('%H:%M:%S'),
            "week": self.tracker.progress["current_week"],
            "stem_id": stem_id,
            "stem_name": stem["name"],
            "prompt": stem["prompt"],
            "completions": completions,
            "completion_count": len(completions)
        }
        
        filename = f"{today.strftime('%Y_%m_%d')}_{stem_id}.yaml"
        filepath = self.journals_dir / filename
        
        with open(filepath, 'w') as f:
            yaml.dump(entry, f)
        
        print(f"Saved {len(completions)} completions to {filepath}")
    
    def get_week_summary(self, week: int) -> List[Dict]:
        """Get all entries for a specific week"""
        week_entries = []
        for file in self.journals_dir.glob("*.yaml"):
            try:
                with open(file, 'r') as f:
                    entry = yaml.safe_load(f)
                    if entry.get("week") == week:
                        week_entries.append(entry)
            except:
                continue
        return week_entries
    
    def show_week_summary(self, week: int):
        """Display summary of week's practice"""
        entries = self.get_week_summary(week)
        if not entries:
            print("No entries found for this week.")
            return
        
        print(f"\nWeek {week} Summary")
        print("=" * 50)
        
        # Group entries by stem
        stems = {}
        total_completions = 0
        
        for entry in entries:
            stem_id = entry.get("stem_id", "unknown")
            if stem_id not in stems:
                stems[stem_id] = {
                    "name": entry.get("stem_name", "Unknown"),
                    "prompt": entry.get("prompt", ""),
                    "completions": []
                }
            
            if "completion" in entry:  # Individual completion
                stems[stem_id]["completions"].append(entry["completion"])
                total_completions += 1
            elif "completions" in entry:  # Old grouped format
                stems[stem_id]["completions"].extend(entry["completions"])
                total_completions += len(entry["completions"])
        
        for stem_id, stem_data in stems.items():
            print(f"\n{stem_data['name']}:")
            print(f"Prompt: {stem_data['prompt']}")
            for i, completion in enumerate(stem_data['completions'], 1):
                print(f"  {i}. {completion}")
        
        print(f"\nTotal completions this week: {total_completions}")
    
    def weekend_reflection(self, exercises: List[Dict]):
        """Handle weekend reflection and compilation"""
        reflection = self.tracker.get_weekend_reflection(exercises)
        if not reflection:
            print("❌ Weekend reflection exercise not found!")
            return
        
        current_week = self.tracker.progress["current_week"]
        
        print("\n🌅 Weekend Reflection")
        print("=" * 50)
        print(f"Reflecting on Week {current_week}")
        
        # Show week summary
        self.show_week_summary(current_week)
        
        print(f"\n{reflection['prompt']}")
        print(f"\nInstructions: {reflection['instructions']}")
        
        print("\nPlease write at least 5 reflections:")
        reflections = []
        for i in range(5):
            reflection_text = input(f"Reflection {i+1}: ")
            if reflection_text.strip():
                reflections.append(reflection_text)
        
        # Save weekend reflection
        today = datetime.now()
        entry = {
            "date": today.strftime('%Y-%m-%d'),
            "time": today.strftime('%H:%M:%S'),
            "week": current_week,
            "type": "weekend_reflection",
            "prompt": reflection["prompt"],
            "reflections": reflections
        }
        
        filename = f"{today.strftime('%Y_%m_%d')}_weekend_reflection_week_{current_week}.yaml"
        filepath = self.journals_dir / filename
        
        with open(filepath, 'w') as f:
            yaml.dump(entry, f)
        
        print(f"✅ Saved weekend reflection to {filepath}")
        
        # Advance to next week
        response = input("\n🤔 Ready to advance to Week {self.tracker.progress['current_week'] + 1}? (y/N): ")
        if response.lower() in ['y', 'yes']:
            self.tracker.advance_week()
            print(f"✅ Advanced to Week {self.tracker.progress['current_week']}")
        else:
            print("⏸️  Staying on current week")
    
    def save_single_completion(self, stem: Dict, completion: str):
        """Save a single sentence completion immediately"""
        today = datetime.now()
        stem_id = stem.get("stem_id", "unknown")
        
        entry = {
            "date": today.strftime('%Y-%m-%d'),
            "time": today.strftime('%H:%M:%S'),
            "week": self.tracker.progress["current_week"],
            "stem_id": stem_id,
            "stem_name": stem["name"],
            "prompt": stem["prompt"],
            "completion": completion
        }
        
        filename = f"{today.strftime('%Y_%m_%d')}_{stem_id}_{len(self.get_todays_completions(stem_id)) + 1}.yaml"
        filepath = self.journals_dir / filename
        
        with open(filepath, 'w') as f:
            yaml.dump(entry, f)
        
        print(f"✅ Saved completion #{len(self.get_todays_completions(stem_id))} to {filepath}")
    
    def get_todays_completions(self, stem_id: str) -> List[Dict]:
        """Get all completions for today's stem"""
        today = datetime.now().strftime('%Y_%m_%d')
        completions = []
        
        for file in self.journals_dir.glob(f"{today}_{stem_id}_*.yaml"):
            try:
                with open(file, 'r') as f:
                    entry = yaml.safe_load(f)
                    completions.append(entry)
            except:
                continue
        
        return completions
    
    def daily_practice(self, exercises: List[Dict]):
        """Handle daily sentence completion practice - ALL stems every morning, 6-10 completions each"""
        current_week = self.tracker.progress["current_week"]
        week_exercises = [ex for ex in exercises if ex.get("week") == current_week and ex.get("type") == "sentence_completion"]
        
        if not week_exercises:
            print("❌ No stems available for this week!")
            return
        
        print(f"\n📝 Morning Practice - Week {current_week}")
        print("=" * 50)
        print(f"Complete ALL {len(week_exercises)} stems this morning (6-10 completions each):")
        print("Work rapidly, don't pause to think. Any ending is fine - just keep going.")
        print("Type 'quit' to exit without saving.")
        
        today = datetime.now()
        all_completions = []
        
        # Process each stem for the week
        for stem_index, stem in enumerate(week_exercises):
            print(f"\n{stem_index + 1}. {stem['name']}")
            print(f"   Prompt: {stem['prompt']}")
            print(f"   Instructions: Write 6-10 completions rapidly, without pausing to think.")
            
            stem_completions = []
            completion_count = 0
            
            while completion_count < 10:  # Allow up to 10 completions
                completion = input(f"   Completion #{completion_count + 1}: ")
                
                if completion.lower() == 'quit':
                    print("❌ Exiting without saving.")
                    return
                
                if completion.strip():
                    stem_completions.append({
                        "stem_id": stem.get("stem_id", "unknown"),
                        "stem_name": stem["name"],
                        "prompt": stem["prompt"],
                        "completion": completion,
                        "completion_number": completion_count + 1
                    })
                    completion_count += 1
                    
                    # Check if user wants to continue after minimum 6
                    if completion_count >= 6:
                        continue_choice = input(f"   Continue? (y/n, or 'done' to finish this stem): ")
                        if continue_choice.lower() in ['n', 'no', 'done']:
                            break
                else:
                    print("⚠️  Empty completion ignored. Type your completion or 'quit'.")
            
            # Save stem completions immediately
            if stem_completions:
                stem_filename = f"{today.strftime('%Y_%m_%d')}_{stem.get('stem_id', f'stem_{stem_index}')}.yaml"
                stem_filepath = self.journals_dir / stem_filename
                
                stem_entry = {
                    "date": today.strftime('%Y-%m-%d'),
                    "time": today.strftime('%H:%M:%S'),
                    "week": current_week,
                    "day_of_week": today.weekday(),
                    "stem": stem,
                    "completions": stem_completions,
                    "total_completions": len(stem_completions)
                }
                
                with open(stem_filepath, 'w') as f:
                    yaml.dump(stem_entry, f)
                
                print(f"✅ Saved {len(stem_completions)} completions for {stem['name']}")
                all_completions.extend(stem_completions)
        
        # Save overall daily summary
        if all_completions:
            summary_filename = f"{today.strftime('%Y_%m_%d')}_week_{current_week}_morning_practice.yaml"
            summary_filepath = self.journals_dir / summary_filename
            
            summary_entry = {
                "date": today.strftime('%Y-%m-%d'),
                "time": today.strftime('%H:%M:%S'),
                "week": current_week,
                "day_of_week": today.weekday(),
                "total_stems": len(week_exercises),
                "total_completions": len(all_completions),
                "stems_completed": [stem["name"] for stem in week_exercises]
            }
            
            with open(summary_filepath, 'w') as f:
                yaml.dump(summary_entry, f)
            
            print(f"\n🎉 Morning practice complete!")
            print(f"✅ Completed {len(week_exercises)} stems with {len(all_completions)} total completions")
            print(f"📁 Saved to: {summary_filepath}")
            print(f"\n📅 Come back tomorrow morning for the same practice!")
            
            # Mark today as completed
            self.tracker.advance_day()
    
    def advance_day(self):
        """Advance to next day (not next stem)"""
        # For now, just track that we completed today
        # The actual day advancement will be handled by the weekend reflection
        pass
    
    def is_week_complete(self):
        """Check if we've completed all days of the current week"""
        # This is a simplified check - in practice, you'd track each day
        return True  # For now, assume week is complete after one session
    
    def show_progress(self):
        """Show current progress"""
        current_week = self.tracker.progress["current_week"]
        current_stem_index = self.tracker.progress.get("current_stem_index", 0)
        start_date = self.tracker.progress.get("start_date", "Unknown")
        is_new_user = self.tracker.progress.get("is_new_user", False)
        
        print(f"\nProgress Report")
        print("=" * 30)
        print(f"Current Week: {current_week}")
        print(f"Current Stem: {current_stem_index + 1}")
        print(f"Started: {start_date}")
        
        if start_date != "Unknown":
            start = date.fromisoformat(start_date)
            days_active = (date.today() - start).days
            print(f"Days Active: {days_active} days")
            
            # Calculate expected progress
            expected_week = (days_active // 7) + 1
            expected_stem = (days_active % 7) + 1
            
            if expected_week != current_week or expected_stem != current_stem_index + 1:
                print(f"Expected Progress: Week {expected_week}, Day {expected_stem}")
                print(f"Note: Progress may be manually adjusted")
        
        if is_new_user:
            print("Status: New user")
        else:
            print("Status: Returning user")
    
    def get_available_exercises(self, exercises: List[Dict]) -> List[Dict]:
        """Get exercises available for today based on time and progress"""
        today = datetime.now()
        current_hour = today.hour
        available = []
        
        # Add morning check-in (available 5 AM - 11 AM)
        if 5 <= current_hour <= 11:
            morning_exercises = [ex for ex in exercises if ex.get("type") == "morning_checkin"]
            available.extend(morning_exercises)
        
        # Add evening reflection (available 6 PM - 11 PM)
        if 18 <= current_hour <= 23:
            evening_exercises = [ex for ex in exercises if ex.get("type") == "evening_reflection"]
            available.extend(evening_exercises)
        
        # Add sentence completion exercises (available all day, but only current week's stems)
        if not self.tracker.is_weekend():
            week_stems = self.tracker.get_week_stems(exercises)
            if week_stems:
                # Add each stem individually as an available exercise
                available.extend(week_stems)
        
        # Add weekend reflection (available on weekends)
        if self.tracker.is_weekend():
            weekend_exercises = [ex for ex in exercises if ex.get("type") == "weekend_reflection"]
            available.extend(weekend_exercises)
        
        return available
    
    def handle_custom_exercise(self, exercise: Dict):
        """Handle custom exercises (morning/evening) with simple text input"""
        print(f"\n📝 {exercise['name']}")
        print("=" * 50)
        print(f"Prompt: {exercise['prompt']}")
        print(f"\nInstructions: {exercise['instructions']}")
        
        response = input("\nYour response: ")
        
        if response.strip():
            # Save the response
            today = datetime.now()
            exercise_type = exercise.get("type", "custom")
            
            entry = {
                "date": today.strftime('%Y-%m-%d'),
                "time": today.strftime('%H:%M:%S'),
                "exercise_name": exercise["name"],
                "exercise_type": exercise_type,
                "prompt": exercise["prompt"],
                "response": response
            }
            
            filename = f"{today.strftime('%Y_%m_%d')}_{exercise_type}.yaml"
            filepath = self.journals_dir / filename
            
            with open(filepath, 'w') as f:
                yaml.dump(entry, f)
            
            print(f"✅ Saved response to {filepath}")
        else:
            print("❌ No response entered.")
    
    def main(self):
        """Main journaling function"""
        print("ENOUGH - Nathaniel Branden Sentence Completion")
        print("=" * 55)
        
        # Handle first-time setup
        if self.tracker.is_first_run():
            self.tracker.initialize_new_user()
        
        # Load exercises
        exercises = self.load_exercises()
        if not exercises:
            print("❌ No exercises found!")
            return
        
        # Show progress
        self.show_progress()
        
        # Get available exercises for today
        available = self.get_available_exercises(exercises)
        
        if not available:
            print("\n📅 No exercises available right now.")
            current_hour = datetime.now().hour
            if current_hour < 5:
                print("💤 Come back after 5 AM for morning check-in.")
            elif current_hour < 18:
                print("📝 Come back during the day for sentence completion practice.")
            else:
                print("🌙 Come back between 6-11 PM for evening reflection.")
            return
        
        # Show available exercises
        print(f"\n📋 Available exercises ({len(available)}):")
        for i, exercise in enumerate(available, 1):
            exercise_type = exercise.get("type", "unknown")
            if exercise_type in ["morning_checkin", "evening_reflection"]:
                print(f"{i}. {exercise['name']} ({exercise_type})")
            else:
                print(f"{i}. {exercise['name']} (sentence completion)")
        
        # Let user choose if multiple exercises available
        if len(available) > 1:
            try:
                choice = int(input(f"\nChoose exercise (1-{len(available)}): ")) - 1
                if choice < 0 or choice >= len(available):
                    print("❌ Invalid choice.")
                    return
                selected_exercise = available[choice]
            except ValueError:
                print("❌ Please enter a number.")
                return
        else:
            selected_exercise = available[0]
        
        # Handle the selected exercise
        exercise_type = selected_exercise.get("type", "unknown")
        
        if exercise_type in ["morning_checkin", "evening_reflection"]:
            self.handle_custom_exercise(selected_exercise)
        elif exercise_type == "weekend_reflection":
            self.weekend_reflection(exercises)
        elif exercise_type == "sentence_completion":
            # For sentence completion, we want to practice all stems for the week
            self.daily_practice(exercises)
        else:
            print(f"❌ Unknown exercise type: {exercise_type}")
        
        # Save progress
        self.tracker.save_progress()

def main():
    """Entry point"""
    journaler = Journaler()
    journaler.main()

if __name__ == '__main__':
    main() 