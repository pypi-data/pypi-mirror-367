#!/usr/bin/env python3
"""
ENOUGH - Nathaniel Branden Sentence Completion Journal
Main application logic
"""

import os
import yaml
import json
import time
from datetime import datetime, timedelta
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
            "last_completed": None
        }
    
    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def update_progress(self, week: int, day: int):
        self.progress["current_week"] = week
        self.progress["current_day"] = day
        self.save_progress()


class Journaler:
    def __init__(self):
        self.tracker = ProgressTracker()
        self.exercises = self.load_exercises()
        self.submissions_dir = "submissions"
        self.session_start_time = None
        os.makedirs(self.submissions_dir, exist_ok=True)
    
    def clear_terminal(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def load_exercises(self) -> List[Dict]:
        """Load all exercises from journals directory"""
        exercises = []
        journals_dir = "journals"
        
        if not os.path.exists(journals_dir):
            print(f"❌ Journals directory '{journals_dir}' not found!")
            return exercises
        
        # Load all .yaml files from journals directory
        for filename in os.listdir(journals_dir):
            if filename.endswith('.yaml'):
                filepath = os.path.join(journals_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        data = yaml.safe_load(f)
                        
                        if data.get('type') == 'branden':
                            # This is a multi-week exercise
                            exercise = {
                                'name': data['name'],
                                'description': data.get('description', ''),
                                'type': 'branden',
                                'weeks': data['total_weeks'],
                                'weeks_data': data['weeks']  # Fixed: was trying to access 'weeks_data' later
                            }
                            exercises.append(exercise)
                            
                        elif data.get('type') == 'custom':
                            # This is a custom exercise
                            exercise = {
                                'name': data['name'],
                                'description': data.get('description', ''),
                                'type': 'custom',
                                'time': data['time'],
                                'stems': data['stems']
                            }
                            exercises.append(exercise)
                            
                except Exception as e:
                    print(f"❌ Failed to load {filename}: {e}")
        
        return exercises
    
    def get_current_exercise(self) -> Optional[Dict]:
        """Get current exercise based on progress"""
        if not self.exercises:
            return None
        
        current_week = self.tracker.progress["current_week"]
        
        # Check if we have a start date to calculate proper week
        if self.tracker.progress.get("start_date"):
            start_date = datetime.strptime(self.tracker.progress["start_date"], "%Y-%m-%d")
            today = datetime.now()
            
            # Calculate weekdays only (Monday-Friday)
            days_since_start = 0
            current_date = start_date
            while current_date <= today:
                if current_date.weekday() < 5:  # Monday = 0, Tuesday = 1, ..., Friday = 4
                    days_since_start += 1
                current_date += timedelta(days=1)
            
            # Calculate week based on weekdays only (6 weekdays per week)
            calculated_week = (days_since_start // 6) + 1
            
            # Use calculated week if it's different from stored week
            if calculated_week != current_week:
                self.tracker.progress["current_week"] = calculated_week
                self.tracker.save_progress()
                current_week = calculated_week
        
        # Find the current branden exercise (assuming it's the first one)
        branden_exercise = None
        for exercise in self.exercises:
            if exercise.get('type') == 'branden':
                branden_exercise = exercise
                break
        
        if not branden_exercise:
            print("❌ No branden exercise found in journals directory")
            return None
        
        # Find the week data - fixed to use 'weeks_data' which contains the 'weeks' list
        for week_data in branden_exercise['weeks_data']:
            if week_data['week'] == current_week:
                return {
                    'week': current_week,
                    'stems': week_data['stems']
                }
        
        # If no exercise found for current week, check if we're beyond the program
        if current_week > branden_exercise['weeks']:
            print(f"✅ Congratulations! You've completed all {branden_exercise['weeks']} weeks of the program.")
            return None
        
        print(f"❌ No exercise found for week {current_week}")
        return None
    
    def handle_first_time_user(self):
        """Handle first-time user setup"""
        print("\n=========================================")
        print("        ENOUGH - Minimal Journal")
        print(" Inspired by Nathaniel Branden's Work")
        print("=========================================")
        print()
        print("No prior journal found for this exercise.")
        print()
        print("Would you like to:")
        print("1. Start from Week 1 | Day 1 (beginner)")
        print("2. Choose a specific week and day")
        print("3. Go back")
        print()
        
        while True:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == "1":
                # Start from Week 1, Day 1
                today = datetime.now()
                
                if today.weekday() >= 5:  # Weekend: Saturday = 5, Sunday = 6
                    print(f"\nYou chose to start from Week 1 | Day 1.")
                    print(f"Today is {today.strftime('%A')}. Exercises begin on Mondays.")
                    print("Come back on Monday to begin Week 1 | Day 1.")
                    return False
                else:
                    # Calculate the start date for Week 1 (go back to Monday of this week)
                    days_since_monday = today.weekday()
                    start_date = today - timedelta(days=days_since_monday)
                    
                    self.tracker.progress["start_date"] = start_date.strftime("%Y-%m-%d")
                    self.tracker.progress["current_week"] = 1
                    self.tracker.progress["current_day"] = 1
                    self.tracker.save_progress()
                    return True
                    
            elif choice == "2":
                print("\nWhat week are you currently on? (1-30): ")
                try:
                    week = int(input().strip())
                    if week < 1 or week > 30:
                        print("Please enter a week between 1 and 30.")
                        continue
                    
                    print("\nEnter a custom start date (YYYY-MM-DD): ")
                    custom_date_str = input().strip()
                    
                    try:
                        custom_date = datetime.strptime(custom_date_str, "%Y-%m-%d")
                        
                        # Check if it's a weekend
                        if custom_date.weekday() >= 5:  # Weekend: Saturday = 5, Sunday = 6
                            print(f"\nThe date you selected falls on a weekend.")
                            print(f"Exercises begin on Mondays. Starting from the next Monday.")
                            
                            # Calculate next Monday
                            days_until_monday = (7 - custom_date.weekday()) % 7
                            if days_until_monday == 0:
                                days_until_monday = 7
                            start_date = custom_date + timedelta(days=days_until_monday)
                        else:
                            start_date = custom_date
                        
                        print(f"Starting from custom week {week}")
                        print(f"Start date calculated: {start_date.strftime('%Y-%m-%d')} ({start_date.strftime('%A')})")
                        
                        self.tracker.progress["start_date"] = start_date.strftime("%Y-%m-%d")
                        self.tracker.progress["current_week"] = week
                        self.tracker.progress["current_day"] = 1
                        self.tracker.save_progress()
                        return True
                        
                    except ValueError:
                        print("❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2025-01-15)")
                        continue
                    
                except ValueError:
                    print("Please enter valid numbers.")
                    continue
            elif choice == "3":
                return False
            else:
                print("Please enter '1', '2', or '3'.")
    
    def check_and_setup_user(self):
        """Check if user needs setup and handle it"""
        # Check if there are any existing submissions for this exercise
        current_week = self.tracker.progress["current_week"]
        
        # Generate exercise name based on actual exercise name
        branden_exercise = None
        for ex in self.exercises:
            if ex.get('type') == 'branden':
                branden_exercise = ex
                break
        
        if not branden_exercise:
            print("❌ No branden exercise found")
            return False
            
        # Use sanitized exercise name for file naming
        exercise_name = branden_exercise['name'].replace(' ', '_').replace('-', '_').lower()
        exercise_name = ''.join(c for c in exercise_name if c.isalnum() or c == '_')
        
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
        """Save submission in standard format: exercisename_datelike210431"""
        # Convert YYYYMMDD to datelike format (e.g., 210431 for 2021-04-31)
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            datelike = date_obj.strftime("%y%m%d")  # YYMMDD format
        except:
            datelike = date_str  # Fallback to original format
        
        filename = f"{exercise_name}_{datelike}.yaml"
        filepath = os.path.join(self.submissions_dir, filename)
        
        # Load existing data if file exists
        existing_data = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    existing_data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"❌ Error reading existing submission file: {e}")
                existing_data = {}
        
        # Calculate session timing
        end_time = datetime.now()
        duration_minutes = 0
        
        if self.session_start_time:
            duration = end_time - self.session_start_time
            duration_minutes = round(duration.total_seconds() / 60, 1)
        
        # Prepare session data
        session_data = {
            "started_at": self.session_start_time.isoformat() if self.session_start_time else datetime.now().isoformat(),
            "ended_at": end_time.isoformat(),
            "duration_minutes": duration_minutes
        }
        
        # If we have existing session data, preserve start time but update end time
        if "session" in existing_data:
            session_data["started_at"] = existing_data["session"].get("started_at", session_data["started_at"])
            # Add to existing duration
            existing_duration = existing_data["session"].get("duration_minutes", 0)
            session_data["duration_minutes"] = existing_duration + duration_minutes
        
        data = {
            "journal": exercise_name,
            "date": date_str,
            "week": self.tracker.progress["current_week"],
            "day": self.tracker.progress["current_day"],
            "session": session_data,
            "submissions": existing_data.get("submissions", {})
        }
        
        # Add the new submission
        data["submissions"][stem] = completions
        
        try:
            with open(filepath, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        except Exception as e:
            print(f"❌ Error saving submission: {e}")
    
    def get_week_submissions(self, exercise_name: str, week_start: str) -> Dict[str, List[str]]:
        """Get all submissions for a week"""
        submissions = {}
        try:
            for i in range(7):
                current_date = datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=i)
                date_str = current_date.strftime("%Y%m%d")
                
                # Convert to datelike format for filename
                try:
                    date_obj = datetime.strptime(date_str, "%Y%m%d")
                    datelike = date_obj.strftime("%y%m%d")  # YYMMDD format
                except:
                    datelike = date_str  # Fallback
                
                filename = f"{exercise_name}_{datelike}.yaml"
                filepath = os.path.join(self.submissions_dir, filename)
                
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r') as f:
                            data = yaml.safe_load(f)
                            if data and "submissions" in data:
                                submissions.update(data["submissions"])
                    except Exception as e:
                        print(f"❌ Error reading submission file {filename}: {e}")
        except Exception as e:
            print(f"❌ Error processing week submissions: {e}")
        
        return submissions
    
    def show_menu(self):
        """Show dynamic menu based on available exercises"""
        print("=========================================")
        print("        ENOUGH - Minimal Journal")
        print(" Inspired by Nathaniel Branden's Work")
        print("=========================================")
        print()
        print("Choose your exercise:")
        
        # List all exercises dynamically
        for i, exercise in enumerate(self.exercises, 1):
            print(f"{i}. {exercise['name']}")
        
        print("X. Analytics & Progress Overview")
        print()
    
    def handle_analytics(self):
        """Show analytics and progress overview"""
        print("=========================================")
        print("            Analytics & Progress")
        print("=========================================")
        print()
        
        # Get basic stats
        total_sessions = 0
        total_stems = 0
        total_duration = 0
        current_streak = self.calculate_streak()
        
        # Count submissions and calculate total time
        for filename in os.listdir(self.submissions_dir):
            if filename.endswith('.yaml'):
                total_sessions += 1
                filepath = os.path.join(self.submissions_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = yaml.safe_load(f)
                        if data and "submissions" in data:
                            total_stems += len(data["submissions"])
                        if data and "session" in data:
                            total_duration += data["session"].get("duration_minutes", 0)
                except Exception as e:
                    print(f"❌ Error reading analytics data: {e}")
        
        # Calculate time spent
        hours = int(total_duration // 60)
        minutes = int(total_duration % 60)
        time_spent = f"{hours} hrs {minutes} mins" if hours > 0 else f"{minutes} mins"
        
        print(f"Journal: Nathaniel Branden - Sentence Completion Exercises")
        print()
        print(f"Total Sessions Completed: {total_sessions}")
        print(f"Total Sentence Stems Completed: {total_stems}")
        print(f"Total Time Spent Journaling: {time_spent}")
        print(f"Current Streak: {current_streak} weeks (6 days/week target)")
        
        if self.tracker.progress.get("start_date"):
            last_completed = self.tracker.progress.get("last_completed", "Never")
            print(f"Last Completed: Week {self.tracker.progress['current_week']} | Day {self.tracker.progress['current_day']} ({last_completed})")
        
        print()
        print("Recent Session Summary:")
        if total_sessions > 0:
            # Get the most recent session
            submission_files = [f for f in os.listdir(self.submissions_dir) if f.endswith('.yaml')]
            if submission_files:
                # Sort by date (extract datelike part and convert back to sortable format)
                def get_sort_key(filename):
                    try:
                        # Extract datelike part (e.g., "210431" from "exercisename_210431.yaml")
                        datelike = filename.split('_')[-1].replace('.yaml', '')
                        if len(datelike) == 6:  # YYMMDD format
                            return datetime.strptime(datelike, "%y%m%d")
                        return datetime.min  # Fallback for invalid format
                    except:
                        return datetime.min
                
                latest_file = max(submission_files, key=get_sort_key)
                filepath = os.path.join(self.submissions_dir, latest_file)
                try:
                    with open(filepath, 'r') as f:
                        data = yaml.safe_load(f)
                        if data and "session" in data:
                            session = data["session"]
                            started_at = datetime.fromisoformat(session["started_at"])
                            ended_at = datetime.fromisoformat(session["ended_at"])
                            duration = session.get("duration_minutes", 0)
                            
                            print(f"- Last Session: {started_at.strftime('%Y-%m-%d')} ({started_at.strftime('%A')})")
                            print(f"- Start Time: {started_at.strftime('%H:%M')}")
                            print(f"- End Time: {ended_at.strftime('%H:%M')}")
                            print(f"- Duration: {duration:.1f} mins")
                except Exception as e:
                    print("- Last Session: Recent")
                    print("- Duration: Variable")
        
        # Show calendar with month selection
        print()
        print("-----------------------------------------")
        self.show_calendar_analytics()
        
        print()
        input("Press Enter to continue...")
    
    def show_calendar_analytics(self):
        """Show calendar with month selection and day viewing"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        print(f"{calendar.month_name[current_month]} {current_year} Activity")
        print()
        
        # Simple calendar representation
        cal = calendar.monthcalendar(current_year, current_month)
        print("Mon  Tue  Wed  Thu  Fri  Sat  Sun")
        for week in cal:
            for day in week:
                if day == 0:
                    print("     ", end="")
                else:
                    # Check if there's a submission for this day
                    date_str = f"{current_year:04d}{current_month:02d}{day:02d}"
                    # Convert to datelike format for filename matching
                    try:
                        date_obj = datetime.strptime(date_str, "%Y%m%d")
                        datelike = date_obj.strftime("%y%m%d")  # YYMMDD format
                    except:
                        datelike = date_str
                    
                    has_submission = any(f"_{datelike}.yaml" in f for f in os.listdir(self.submissions_dir))
                    if has_submission:
                        print("  x  ", end="")
                    else:
                        print(f"  {day:2d} ", end="")
            print()
        
        print()
        print("Legend:")
        print("- x = Completed session")
        print("- (blank) = No activity")
        print("- 6 sessions per week required to maintain streak")
        
        # Ask for month selection or day viewing
        print()
        print("Options:")
        print("1. View different month")
        print("2. View specific day's submissions")
        print("3. Back to main menu")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            self.select_month_view()
        elif choice == "2":
            self.view_day_submissions()
    
    def select_month_view(self):
        """Allow user to select a different month to view"""
        print("\nEnter month (1-12) and year (YYYY):")
        try:
            month = int(input("Month: ").strip())
            year = int(input("Year: ").strip())
            
            if 1 <= month <= 12 and 2020 <= year <= 2030:
                print(f"\n{calendar.month_name[month]} {year} Activity")
                print()
                
                cal = calendar.monthcalendar(year, month)
                print("Mon  Tue  Wed  Thu  Fri  Sat  Sun")
                for week in cal:
                    for day in week:
                        if day == 0:
                            print("     ", end="")
                        else:
                            date_str = f"{year:04d}{month:02d}{day:02d}"
                            # Convert to datelike format for filename matching
                            try:
                                date_obj = datetime.strptime(date_str, "%Y%m%d")
                                datelike = date_obj.strftime("%y%m%d")  # YYMMDD format
                            except:
                                datelike = date_str
                            
                            has_submission = any(f"_{datelike}.yaml" in f for f in os.listdir(self.submissions_dir))
                            if has_submission:
                                print("  x  ", end="")
                            else:
                                print(f"  {day:2d} ", end="")
                    print()
            else:
                print("❌ Invalid month or year")
        except ValueError:
            print("❌ Please enter valid numbers")
    
    def view_day_submissions(self):
        """View submissions for a specific day"""
        print("\nEnter date (YYYY-MM-DD):")
        try:
            date_str = input().strip()
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            file_date_str = target_date.strftime("%Y%m%d")
            
            # Convert to datelike format for filename
            try:
                date_obj = datetime.strptime(file_date_str, "%Y%m%d")
                datelike = date_obj.strftime("%y%m%d")  # YYMMDD format
            except:
                datelike = file_date_str
            
            # Find submission file for this date
            submission_file = None
            for filename in os.listdir(self.submissions_dir):
                if filename.endswith('.yaml') and f"_{datelike}.yaml" in filename:
                    submission_file = filename
                    break
            
            if submission_file:
                filepath = os.path.join(self.submissions_dir, submission_file)
                try:
                    with open(filepath, 'r') as f:
                        data = yaml.safe_load(f)
                        if data and "submissions" in data:
                            print(f"\nSubmissions for {date_str}:")
                            print("=" * 50)
                            for stem, completions in data["submissions"].items():
                                print(f"\nStem: {stem}")
                                for i, completion in enumerate(completions, 1):
                                    print(f"{i}. {completion}")
                            
                            if "session" in data:
                                session = data["session"]
                                print(f"\nSession Duration: {session.get('duration_minutes', 0):.1f} minutes")
                        else:
                            print("❌ No submissions found for this date")
                except Exception as e:
                    print(f"❌ Error reading submission file: {e}")
            else:
                print("❌ No submissions found for this date")
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD")
    
    def get_user_completions(self, stem: str) -> List[str]:
        """Get user completions with proper UX"""
        completions = []
        print(f"\n{stem}")
        print("Enter at least 6 responses (or type submit to continue when ready):")
        
        # Wait 2 seconds, then clear terminal
        time.sleep(2)
        self.clear_terminal()
        
        print(f"\n{stem}")
        print("Enter at least 6 responses (or type submit to continue when ready):")
        
        while len(completions) < 10:
            completion = input(f"{len(completions) + 1}. ").strip()
            
            if completion == "submit":  # No quotes, exact match
                if len(completions) >= 6:
                    break
                else:
                    print("Must submit at least 6 endings")
                    continue
            
            if completion:
                completions.append(completion)
        
        print("✔️ Submission accepted. Proceeding to next sentence stem...")
        time.sleep(2)
        self.clear_terminal()
        
        return completions
    
    def handle_weekend_reflection(self, exercise: Dict, week_start: str):
        """Handle weekend reflection - one of the main features"""
        # Start session timing
        self.session_start_time = datetime.now()
        
        current_week = self.tracker.progress["current_week"]
        current_day = self.tracker.progress["current_day"]
        
        print(f"\nWeek {current_week} | Day {current_day}")
        print()
        print("Reflect on this weeks submissions.")
        print("Enter at least 6 responses (or type submit to continue when ready):")
        
        # Wait 2 seconds, then clear terminal
        time.sleep(2)
        self.clear_terminal()
        
        # Generate exercise name based on actual exercise name
        branden_exercise = None
        for ex in self.exercises:
            if ex.get('type') == 'branden':
                branden_exercise = ex
                break
        
        if not branden_exercise:
            print("❌ No branden exercise found")
            return
            
        # Use sanitized exercise name for file naming
        exercise_name = branden_exercise['name'].replace(' ', '_').replace('-', '_').lower()
        exercise_name = ''.join(c for c in exercise_name if c.isalnum() or c == '_')
        
        submissions = self.get_week_submissions(exercise_name, week_start)
        
        if not submissions:
            print("No submissions found for this week. Starting fresh reflection...")
            reflection_stem = "If I reflect on my week..."
            print(f'"{reflection_stem}"')
            print()
            reflection_completions = self.get_user_completions(reflection_stem)
            
            # Save weekend reflection
            current_date = datetime.now().strftime("%Y%m%d")
            self.save_submission(exercise_name, current_date, reflection_stem, reflection_completions)
            
            # Update last completed
            self.tracker.progress["last_completed"] = datetime.now().strftime("%Y-%m-%d")
            self.tracker.save_progress()
            return
        
        # Handle partial weeks - compile whatever exists
        print(f"Found {len(submissions)} stems with submissions this week.")
        print("Reflecting on your week's work...")
        
        for stem, completions in submissions.items():
            print(f"\nWeek {current_week} | Day {current_day} - Reflect")
            print()
            print(f'"{stem}"')
            print()
            
            # Show their submissions for this week
            for i, completion in enumerate(completions, 1):
                print(f"{i}. {completion}")
            
            print()
            reflection_stem = "If any of what I have been writing this week is true..."
            print(f'"{reflection_stem}"')
            print()
            reflection_completions = self.get_user_completions(reflection_stem)
            
            # Save weekend reflection
            current_date = datetime.now().strftime("%Y%m%d")
            self.save_submission(exercise_name, current_date, reflection_stem, reflection_completions)
        
        # Update last completed
        self.tracker.progress["last_completed"] = datetime.now().strftime("%Y-%m-%d")
        self.tracker.save_progress()
    
    def run_custom_exercise(self, exercise: Dict):
        """Run a custom exercise"""
        # Start session timing
        self.session_start_time = datetime.now()
        
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
        
        # Update last completed
        self.tracker.progress["last_completed"] = datetime.now().strftime("%Y-%m-%d")
        self.tracker.save_progress()

    def run_exercise(self, exercise: Dict):
        """Run the main branden exercise"""
        current_week = self.tracker.progress["current_week"]
        current_day = self.tracker.progress["current_day"]
        
        # Start session timing
        self.session_start_time = datetime.now()
        
        print(f"\nWeek {current_week} | Day {current_day}")
        
        # Generate exercise name based on actual exercise name
        branden_exercise = None
        for ex in self.exercises:
            if ex.get('type') == 'branden':
                branden_exercise = ex
                break
        
        if not branden_exercise:
            print("❌ No branden exercise found")
            return
            
        # Use sanitized exercise name for file naming
        exercise_name = branden_exercise['name'].replace(' ', '_').replace('-', '_').lower()
        exercise_name = ''.join(c for c in exercise_name if c.isalnum() or c == '_')
        
        # Check if it's weekend
        today = datetime.now()
        if today.weekday() >= 5:  # Weekend: Saturday = 5, Sunday = 6
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
            
            # Update progress and last completed
            self.tracker.progress["last_completed"] = datetime.now().strftime("%Y-%m-%d")
            
            if current_stem_index == len(stems) - 1:
                # Move to next week
                self.tracker.update_progress(current_week + 1, 1)
            else:
                # Move to next day
                self.tracker.update_progress(current_week, current_day + 1)
    
    def calculate_streak(self) -> int:
        """Calculate current streak based on submission patterns"""
        if not self.tracker.progress.get("start_date"):
            return 0
        
        start_date = datetime.strptime(self.tracker.progress["start_date"], "%Y-%m-%d")
        today = datetime.now()
        
        # Get all submission files
        submission_files = []
        for filename in os.listdir(self.submissions_dir):
            if filename.endswith('.yaml'):
                submission_files.append(filename)
        
        if not submission_files:
            return 0
        
        # Sort files by date
        submission_files.sort()
        
        # Calculate weeks with sufficient sessions (6+ per week)
        current_streak = 0
        max_streak = 0
        
        # Group submissions by week
        week_submissions = {}
        for filename in submission_files:
            try:
                # Extract date from filename (format: exercisename_YYMMDD.yaml)
                date_part = filename.split('_')[-1].replace('.yaml', '')
                if len(date_part) == 6:  # YYMMDD format
                    file_date = datetime.strptime(date_part, "%y%m%d")
                    week_start = file_date - timedelta(days=file_date.weekday())
                    week_key = week_start.strftime("%Y-%m-%d")
                    
                    if week_key not in week_submissions:
                        week_submissions[week_key] = 0
                    week_submissions[week_key] += 1
            except:
                continue
        
        # Calculate streak
        sorted_weeks = sorted(week_submissions.keys())
        for week in sorted_weeks:
            if week_submissions[week] >= 6:  # 6+ sessions per week
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def main(self):
        """Main application loop"""
        # Check if exercises were loaded successfully
        if not self.exercises:
            print("❌ No exercises found in journals directory!")
            print("Please ensure you have .yaml files in the 'journals' directory.")
            return
        
        while True:
            try:
                self.show_menu()
                choice = input("Enter your choice: ").strip().upper()
                
                if choice == "X":
                    self.handle_analytics()
                    continue
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(self.exercises):
                        selected_exercise = self.exercises[choice_num - 1]
                        
                        if selected_exercise.get('type') == 'branden':
                            # Check if user needs setup for this specific exercise
                            if not self.check_and_setup_user():
                                continue
                            
                            exercise = self.get_current_exercise()
                            if exercise:
                                self.run_exercise(exercise)
                            else:
                                print("No exercise found for current week")
                        else:
                            # Custom exercise
                            self.run_custom_exercise(selected_exercise)
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("Please try again.")


def main():
    journaler = Journaler()
    journaler.main()


if __name__ == "__main__":
    main() 