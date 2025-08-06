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

## Features

- **Minimal Interface**: Clean, distraction-free experience
- **Progress Tracking**: Automatic week and day progression
- **Flexible Practice**: Complete stems at your own pace
- **Local Storage**: All data stored locally on your machine

## License

CC0 1.0 Universal - Public Domain Dedication 