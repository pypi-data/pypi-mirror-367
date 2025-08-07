# ENOUGH - Nathaniel Branden Sentence Completion Journal

A minimal, focused journaling application based on Nathaniel Branden's sentence completion exercises for personal growth and self-awareness.

## Installation

```bash
pip install enough-journal
```
or AUR, add AUR how to install on arch
## Usage

```bash
# Run the journal
python -m enough
```

Upon starting the program it should check the files associated with the exercises. If the program can't find a starting date to certain journals, when choosing that journal it will prompt the user to start from a custom date or start from day 1. 

Upon start the user will meet the following. 

Enough - Minimal Mindfulness Journal inspired by Nathaniel Branden

Choose Your exercise: 
1. Nathanial Branden - Sentence Completion Exercises from the Six Pillars of Self Esteem
2. Custom Exercise Name here
3. Custom Exercise Name here
X. for analytics. --> this will ask for an exercise and show streaks, completions and so on. Streaks are counted even if we skip 1 day of the week. for example sunday, as only 6 exercises per week.

Let's say we choose 1. 

We either prompt the user to choose a week and day or start from day 1 (should handle first day being on weekend by skipping to monday - come back monday), or if he has already a start date logged we do: 

Week 1  |  Day 3

If I paid 5% more energy to my family today... 
- the user is to submit 6 to 10 submissions
- after reaching 10 the system automatically goes to the next question or
- if he types "submit" without "" we will check if he met the minimum 6 then let them go on.
- There are about 4-6 sentence stems for each day.

If it is the weekend we are compiling their answers to each sentence stem they have submitted that week and we show them. You were writing such and such for this question: list their answers that week, so 5 answers and they are to submit 6 additional answers saying "If any of what I have been writing this week is true.." then same submit or 10 submissions logic and go to the next sentence stem that week until the end. That is all.

That is all of what the program should do.

It should also provide analytics. Print a calendar of the current month, be able to choose a month, be able to look at a certain days submission from this screen.

Yaml files should be easy to read and contain all what we need start date, create separate files in the submission folder in this format: exercisename_datelike210431. In this you should have their submissions, saving per each sentence and from this you should resolve the compiling process.


Examples: 

At startup: 

```
=========================================
        ENOUGH - Minimal Journal
 Inspired by Nathaniel Branden's Work
=========================================

Choose your exercise:

1. Nathaniel Branden - Sentence Completion Exercises  (name of the yaml file inside of journals folder)
2. Custom Journal: [Name sourced from the yaml file]  
3. Custom Journal: [Name sourced from the yaml file]  
X. Analytics & Progress Overview

Enter your choice (1-3, or X): 
```

First time running that journal:

```
-----------------------------------------
Nathaniel Branden - Sentence Completion
-----------------------------------------

No prior journal found for this exercise.

Would you like to:

1. Start from Day 1 (auto-starts on the next Monday)  
2. Choose a custom start date  
3. Go back

Enter your choice (1-3): 
```

If the user chooses 1 and today is Saturday or Sunday, respond with:

```
You chose to start from Day 1.

Today is [Saturday/Sunday]. Exercises begin on Mondays.
Come back on Monday to begin Week 1 | Day 1.
```

If today is a weekday (Mon–Fri), begin immediately:
```
Week 1 | Day 1

Sentence Stem 1:
"If I paid 5% more attention to my feelings today..."

Enter response 1 of 6 (type 'submit' when done):
```

If the user selects 2 (custom date), prompt:
```
Enter a custom start date (YYYY-MM-DD): 
Then validate and:
```
If valid and not a weekend, start from that date.
If it's a weekend, respond:

```
The date you selected falls on a weekend.
Exercises begin on Mondays. Starting from the next Monday: YYYY-MM-DD.
```

Example of an actual submission session for the weekday: 
```
Week 1 | Day 1

Enter at least 6 responses (or type 'submit' to continue when ready):
# wait for 2 seconds after printing this message, then clear the terminal
Week 1 | Day 1
"If I bring more awareness to my life today…"


1. I might notice how often I drift into autopilot. #Simply presses enter 
2. I might be more intentional in my conversations.  
3. I might catch myself reacting emotionally before pausing.  
4. I might appreciate small moments more deeply.  
5. I might be less distracted by noise and more focused on what matters.  
6. I might realize I'm doing better than I thought.

#If they Type 'submit' before this point they will get: "Must submit at least 6 endings" 

✔️ Submission accepted. Proceeding to next sentence stem...
# wait for 2 seconds after this message, then clear the terminal and go to next stem like so

Week 1 | Day 1
"If I take more responsibility for my choices and actions today…"


1. I might notice...   #so on..
```

Example of an actual submission session for the weekend:
```
Week 1 | Day 6

Reflect on this weeks submissions.
Enter at least 6 responses (or type 'submit' to continue when ready):
# wait for 2 seconds after printing this message, then clear the terminal

Week 1 | Day 6 - Reflect

"If I bring more awareness to my life today…"

1. I might notice how often I drift into autopilot.
2. I might be more intentional in my conversations.  
3. I might catch myself reacting emotionally before pausing.  
4. I might appreciate small moments more deeply.  
5. I might be less distracted by noise and more focused on what matters.  
6. I might realize I'm doing better than I thought.

#notice how above are their submissions for this week.

If any of what I have been writing this week is ture...

1. I need to figure out a way to snap back to reality. 
2. I need to... #same 6 or 10 submission logic as for the weekday.
```

Analytics example: 
```
=========================================
            Analytics & Progress
=========================================

Journal: Nathaniel Branden - Sentence Completion Exercises

Total Sessions Completed: 18
Total Sentence Stems Completed: 54
Total Time Spent Journaling: 6 hrs 32 mins

Current Streak: 2 weeks (6 days/week target)
Last Completed: Week 2 | Day 3 (2025-08-05)

Recent Session Summary:
- Last Session: 2025-08-05 (Tuesday)
- Start Time: 07:42
- End Time: 08:03
- Duration: 21 mins

-----------------------------------------
August 2025 Activity

Mon  Tue  Wed  Thu  Fri  Sat  Sun  
  x    x    x    x    x         .  
  x    x    x                  
                                  

Legend:
- x = Completed session
- . = Reflection submitted
- (blank) = No activity
- 6 sessions per week required to maintain streak
```
Example yaml file in the journal folder:

```
name: Nathaniel Branden - Sentence Completion Exercises
start_date: 2025-08-11  # Always a Monday
weeks:
  Week 1:
    ID1: If I bring more awareness to my life today…
    ID2: If I take more responsibility for my choices and actions today…
    ID3: If I pay more attention to how I deal with people today…
    ID4: If I boost my energy level by 5 percent today…

  Week 2:
    ID5: If I bring 5 percent more awareness to my important relationships…
    ID6: If I bring 5 percent more awareness to my insecurities…
    ID7: If I bring 5 percent more awareness to my deepest needs and wants…
    ID8: If I bring 5 percent more awareness to my emotions…

  Week 3:
    ID9: If I treat listening as a creative act…
    ID10: If I notice how people are affected by the quality of my listening…
    ID11: If I bring more awareness to my dealings with people today…
    ID12: If I commit to dealing with people with fairness and kindness…

  Week 4:
    ID13: If I bring a higher level of self-esteem to my activities today…
    ID14: If I bring a higher level of self-esteem to my dealings with people today…
    ID15: If I am 5 percent more self-accepting today…
    ID16: If I am self-accepting even when I make mistakes…
    ID17: If I am self-accepting even when I feel confused and overwhelmed…
```

Log file example: 
```
journal: Nathaniel Branden - Sentence Completion Exercises
date: 2025-08-05
week: 1
day: 1

session:
  started_at: 2025-08-05T07:42:10  # ISO 8601
  ended_at: 2025-08-05T08:03:52
  duration_minutes: 21.7

submissions:
  ID1:
    stem: If I bring more awareness to my life today…
    responses:
      - ...
  ID2:
    stem: If I take more responsibility for my choices and actions today…
    responses:
      - ...
  ID3:
    stem: If I pay more attention to how I deal with people today…
    responses:
      - ...
  ID4:
    stem: If I boost my energy level by 5 percent today…
    responses:
      - ...
```


## Features

- **Minimal Interface**: Clean, distraction-free experience
- **Progress Tracking**: Automatic week and day progression
- **Flexible Practice**: Complete stems at your own pace
- **Local Storage**: All data stored locally on your machine

## License

CC0 1.0 Universal - Public Domain Dedication 