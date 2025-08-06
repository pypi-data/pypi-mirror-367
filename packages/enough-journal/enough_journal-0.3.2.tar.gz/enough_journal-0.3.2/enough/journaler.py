#!/usr/bin/env python3
"""
ENOUGH - Nathaniel Branden Sentence Completion Journal
Main application logic
"""

import os
import yaml
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import calendar


class ProgressTracker:
    def __init__(self, progress_file: str = "progress.json"):
        self.progress_file = progress_file
        self.progress = self.load_progress()
    
    def load_progress(self) -> Dict:
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "current_week": 1,
            "current_day": 1,
            "start_date": None,
            "is_new_user": True
        }
    
    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def update_progress(self, week: int, day: int):
        self.progress["current_week"] = week
        self.progress["current_day"] = day
        self.progress["is_new_user"] = False
        self.save_progress()


class Journaler:
    def __init__(self):
        self.tracker = ProgressTracker()
        self.exercises = self.load_exercises()
        self.submissions_dir = "submissions"
        os.makedirs(self.submissions_dir, exist_ok=True)
    
    def load_exercises(self) -> List[Dict]:
        try:
            # First try to load from package directory
            import pkg_resources
            exercises_file = pkg_resources.resource_filename('enough', 'exercises.yaml')
            with open(exercises_file, 'r') as f:
                data = yaml.safe_load(f)
                return data.get("exercises", [])
        except (FileNotFoundError, ImportError):
            try:
                # Fallback to local directory
                with open("journals/exercises.yaml", 'r') as f:
                    data = yaml.safe_load(f)
                    return data.get("exercises", [])
            except FileNotFoundError:
                print("exercises.yaml not found!")
                return []
    
    def get_current_exercise(self) -> Optional[Dict]:
        if not self.exercises:
            return None
        
        current_week = self.tracker.progress["current_week"]
        
        # Check if we have a start date to calculate proper week
        if self.tracker.progress.get("start_date"):
            start_date = datetime.strptime(self.tracker.progress["start_date"], "%Y-%m-%d")
            today = datetime.now()
            days_since_start = (today - start_date).days
            calculated_week = (days_since_start // 7) + 1
            
            # Use calculated week if it's different from stored week
            if calculated_week != current_week:
                self.tracker.progress["current_week"] = calculated_week
                self.tracker.save_progress()
                current_week = calculated_week
        
        # Find exercise for current week
        for exercise in self.exercises:
            if exercise.get("week") == current_week:
                return exercise
        
        # If no exercise found for current week, check if we're beyond the program
        if current_week > 30:
            print(f"You've completed all 30 weeks! Current week: {current_week}")
            return None
        
        return None
    
    def handle_first_time_user(self):
        """Handle first-time user setup"""
        print("\nWelcome to ENOUGH!")
        print("This is your first time using this exercise.")
        print()
        print("Choose your starting option:")
        print("1. Start from day 1 (today)")
        print("2. Choose custom week and day")
        print()
        
        while True:
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice == "1":
                # Start from today, but handle weekend
                today = datetime.now()
                if today.weekday() >= 5:  # Weekend
                    print("It's the weekend. We'll start fresh on Monday.")
                    # Calculate next Monday
                    days_until_monday = (7 - today.weekday()) % 7
                    if days_until_monday == 0:
                        days_until_monday = 7
                    start_date = today + timedelta(days=days_until_monday)
                else:
                    start_date = today
                
                self.tracker.progress["start_date"] = start_date.strftime("%Y-%m-%d")
                self.tracker.progress["current_week"] = 1
                self.tracker.progress["current_day"] = 1
                self.tracker.save_progress()
                return True
                
            elif choice == "2":
                # Let user choose custom week and day
                print("\nEnter custom starting point:")
                try:
                    week = int(input("Week (1-11): "))
                    day = int(input("Day (1-6): "))
                    
                    if 1 <= week <= 11 and 1 <= day <= 6:
                        self.tracker.progress["current_week"] = week
                        self.tracker.progress["current_day"] = day
                        self.tracker.progress["start_date"] = datetime.now().strftime("%Y-%m-%d")
                        self.tracker.save_progress()
                        return True
                    else:
                        print("Invalid week or day. Please try again.")
                        continue
                except ValueError:
                    print("Please enter valid numbers.")
                    continue
            else:
                print("Please enter '1' or '2'.")
    
    def check_and_setup_user(self):
        """Check if user needs setup and handle it"""
        # Check if there are any existing submissions for this exercise
        current_week = self.tracker.progress["current_week"]
        exercise_name = f"branden_week_{current_week}"
        
        # Check if any submission files exist for this exercise
        has_existing_submissions = False
        for filename in os.listdir(self.submissions_dir):
            if filename.startswith(f"{exercise_name}_") and filename.endswith(".yaml"):
                has_existing_submissions = True
                break
        
        if not has_existing_submissions:
            return self.handle_first_time_user()
        return True
    
    def save_submission(self, exercise_name: str, date_str: str, stem: str, completions: List[str]):
        # Format: exercisename_datelike210431
        filename = f"{exercise_name}_{date_str}.yaml"
        filepath = os.path.join(self.submissions_dir, filename)
        
        data = {
            "date": date_str,
            "exercise": exercise_name,
            "submissions": {
                stem: completions
            }
        }
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                existing_data = yaml.safe_load(f) or {}
                if "submissions" not in existing_data:
                    existing_data["submissions"] = {}
                existing_data["submissions"][stem] = completions
                data = existing_data
        
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def get_week_submissions(self, exercise_name: str, week_start: str) -> Dict[str, List[str]]:
        submissions = {}
        for i in range(7):
            current_date = datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=i)
            date_str = current_date.strftime("%Y%m%d")
            filename = f"{exercise_name}_{date_str}.yaml"
            filepath = os.path.join(self.submissions_dir, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and "submissions" in data:
                        submissions.update(data["submissions"])
        
        return submissions
    
    def show_menu(self):
        print("ENOUGH - Minimal Mindfulness Journal inspired by Nathaniel Branden")
        print()
        print("Choose Your exercise:")
        print("1. Nathaniel Branden - Sentence Completion Exercises from the Six Pillars of Self Esteem")
        print("2. Morning Check-in")
        print("3. Afternoon Reflection")
        print("X. for analytics")
        print()
    
    def handle_analytics(self):
        print("Analytics - Coming soon")
        print("This will show streaks, completions, and calendar view")
    
    def get_user_completions(self, stem: str) -> List[str]:
        completions = []
        print(f"\n{stem}")
        print("Enter 6-10 completions (type 'submit' when done):")
        
        while len(completions) < 10:
            completion = input(f"{len(completions) + 1}. ").strip()
            
            if completion.lower() == "submit":
                if len(completions) >= 6:
                    break
                else:
                    print("Minimum 6 completions required. Continue or type 'submit' again.")
                    continue
            
            if completion:
                completions.append(completion)
        
        return completions
    
    def handle_weekend_reflection(self, exercise: Dict, week_start: str):
        print("\nWeekend Reflection")
        print("Compiling your answers from this week:")
        
        current_week = self.tracker.progress["current_week"]
        exercise_name = f"branden_week_{current_week}"
        
        submissions = self.get_week_submissions(exercise_name, week_start)
        
        for stem, completions in submissions.items():
            print(f"\nFor: {stem}")
            for i, completion in enumerate(completions, 1):
                print(f"  {i}. {completion}")
            
            reflection_stem = "If any of what I have been writing this week is true..."
            print(f"\n{reflection_stem}")
            reflection_completions = self.get_user_completions(reflection_stem)
            
            # Save weekend reflection
            current_date = datetime.now().strftime("%Y%m%d")
            self.save_submission(exercise_name, current_date, reflection_stem, reflection_completions)
    
    def run_custom_exercise(self, exercise: Dict):
        """Run a custom exercise (morning/afternoon)"""
        print(f"\n{exercise['name']}")
        print("=" * 50)
        
        exercise_name = f"custom_{exercise['time']}"
        current_date = datetime.now().strftime("%Y%m%d")
        
        # Run all stems for custom exercises
        for i, stem in enumerate(exercise["stems"], 1):
            print(f"\nStem {i}: {stem}")
            completions = self.get_user_completions(stem)
            
            # Save submission
            self.save_submission(exercise_name, current_date, stem, completions)
        
        print(f"\n✅ Completed {exercise['name']}")

    def run_exercise(self, exercise: Dict):
        current_week = self.tracker.progress["current_week"]
        current_day = self.tracker.progress["current_day"]
        
        print(f"\nWeek {current_week} | Day {current_day}")
        
        # Generate exercise name based on week
        exercise_name = f"branden_week_{current_week}"
        
        # Check if it's weekend
        today = datetime.now()
        if today.weekday() >= 5:  # Saturday = 5, Sunday = 6
            week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
            self.handle_weekend_reflection(exercise, week_start)
            return
        
        # Handle regular weekday
        stems = exercise["stems"]
        current_stem_index = (current_day - 1) % len(stems)
        
        if current_stem_index < len(stems):
            stem = stems[current_stem_index]
            completions = self.get_user_completions(stem)
            
            # Save submission
            current_date = datetime.now().strftime("%Y%m%d")
            self.save_submission(exercise_name, current_date, stem, completions)
            
            # Update progress
            if current_stem_index == len(stems) - 1:
                # Move to next week
                self.tracker.update_progress(current_week + 1, 1)
            else:
                # Move to next day
                self.tracker.update_progress(current_week, current_day + 1)
    
    def main(self):
        while True:
            self.show_menu()
            choice = input("Enter your choice: ").strip().upper()
            
            if choice == "X":
                self.handle_analytics()
                continue
            
            if choice == "1":
                # Check if user needs setup for this specific exercise
                if not self.check_and_setup_user():
                    continue
                
                exercise = self.get_current_exercise()
                if exercise:
                    self.run_exercise(exercise)
                else:
                    print("No exercise found for current week")
            elif choice == "2":
                # Morning Check-in
                morning_exercise = next((ex for ex in self.exercises if ex.get("type") == "custom" and ex.get("time") == "morning"), None)
                if morning_exercise:
                    self.run_custom_exercise(morning_exercise)
                else:
                    print("Morning exercise not found")
            elif choice == "3":
                # Afternoon Reflection
                afternoon_exercise = next((ex for ex in self.exercises if ex.get("type") == "custom" and ex.get("time") == "afternoon"), None)
                if afternoon_exercise:
                    self.run_custom_exercise(afternoon_exercise)
                else:
                    print("Afternoon exercise not found")
            else:
                print("Invalid choice. Please try again.")


def main():
    journaler = Journaler()
    journaler.main()


if __name__ == "__main__":
    main() 