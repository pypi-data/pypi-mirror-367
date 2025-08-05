

# ENOUGH - The Growth Journal

A command-line tool for personal development through structured journaling and reflection exercises, with a particular focus on the **Nathaniel Branden sentence completion method**.

## What This Is

ENOUGH is a minimal journaling application that guides you through a 30-week program of sentence completion exercises designed to build self-esteem and personal awareness. Based on the work of Nathaniel Branden, each exercise presents an incomplete sentence that you complete with your own thoughts and feelings.

## The Method

**Nathaniel Branden Sentence Completion Method:**
- **Every morning (Monday-Friday)**: Complete ALL stems for that week
- **Each stem**: 6-10 rapid completions (work quickly, don't pause to think)
- **Weekend**: Reflect and compile your responses
- **Duration**: 30 weeks of progressive exercises

**Example Week 1:**
- Monday: Complete all 4 stems (6-10 completions each)
- Tuesday: Complete all 4 stems again (6-10 completions each)
- Wednesday: Complete all 4 stems again (6-10 completions each)
- Thursday: Complete all 4 stems again (6-10 completions each)
- Friday: Complete all 4 stems again (6-10 completions each)
- Weekend: Reflect and compile

## Program Structure

- **30 weeks** of progressive exercises
- **142+ sentence stems** organized by theme
- **Daily practice** (Monday-Friday)
- **Weekly assessment** (Weekend reflection)
- **Progress tracking** with automatic week/day calculation

## Usage

```bash
# Install
pip install enough-journal

# Run
enough-journal
# or
python journaler.py
```

## Exercise Format

Each exercise includes:
- **Prompt**: The incomplete sentence to complete
- **Instructions**: How to approach the exercise
- **Frequency**: Daily (morning/evening) or weekly
- **Type**: Sentence completion, morning check-in, evening reflection

## Data Format

**Progress Tracking** (`progress.json`):
```json
{
  "current_week": 1,
  "current_stem_index": 0,
  "start_date": "2025-01-01",
  "completed_days": [],
  "is_new_user": true
}
```

**Journal Entries** (`journals/YYYY_MM_DD_STEMID.yaml`):
```yaml
date: "2025-01-01"
time: "08:30:00"
week: 1
stem_id: "ID1"
completions:
  - completion: "I would notice the small moments of joy"
    completion_number: 1
  - completion: "I would be more present in conversations"
    completion_number: 2
```

## Frequencies

- **Daily**: Morning check-in (5-11 AM), Evening reflection (6-11 PM)
- **Weekly**: Sentence completion exercises (all day, Monday-Friday)
- **Weekend**: Reflection and compilation exercises

## Dependencies

- Python 3.8+
- PyYAML 6.0.0+

## The Philosophy

This tool embodies the principle that **consistent, structured self-reflection leads to personal growth**. By practicing the Nathaniel Branden sentence completion method daily, you develop:

- **Self-awareness**: Understanding your thoughts and feelings
- **Self-responsibility**: Taking ownership of your choices
- **Self-acceptance**: Embracing your authentic self
- **Self-esteem**: Building confidence through practice

## What Makes This Different

- **Minimal design**: Focus on the practice, not the interface
- **Immediate saving**: Each completion saved instantly
- **Progress tracking**: Automatic week/day calculation
- **Time-based availability**: Exercises appear when appropriate
- **First-run setup**: Smooth onboarding for new users
- **Correct implementation**: True to Nathaniel Branden's method

## Installation

### From PyPI
```bash
pip install enough-journal
```

### From Source
```bash
git clone https://github.com/sipistab/enough
cd enough
python journaler.py
```

### From AUR (Arch Linux)
```bash
yay -S enough-journal
```

---

**Remember**: The goal is not perfection, but consistent practice. Show up every morning, complete your stems, and trust the process. 