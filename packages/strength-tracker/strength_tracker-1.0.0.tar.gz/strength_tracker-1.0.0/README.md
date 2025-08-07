# StrengthTracker

StrengthTracker is a comprehensive, terminal-based workout tracking application for Mark Rippetoe's Starting Strength program. It tracks linear progression, manages deloads, calculates warmup sets, and maintains detailed workout history.

## Features

- **Linear Progression Tracking**: Automatically increases weights after successful workouts
- **Smart Deload Management**: Handles failed sets with configurable deload logic
- **Automatic Warmup Calculations**: Generates appropriate warmup sets for main lifts
- **Workout Scheduling**: Determines which workout is due based on the current week
- **Progress Analytics**: View workout history and current weights with detailed breakdowns
- **Local Data Storage**: All data stored in human-readable YAML format
- **Cross-platform**: Works on Windows, Mac, and Linux
- **Minimal Dependencies**: Just Python and a few lightweight packages

## Installation

### From PyPI (Recommended)
```bash
pip install strength-tracker
```

### From AUR (Arch User Repository)
```bash
# Using yay (recommended)
yay -S strength-tracker

# Using paru
paru -S strength-tracker
```

### From Source
```bash
# Clone the repository
git clone https://github.com/sipistab/strength-tracker.git
cd strength-tracker

# Install dependencies
pip install -r requirements.txt

# Install as a module
pip install -e .
```

## Usage

Run StrengthTracker:
```bash
python -m strength-tracker
```

The application will check for existing workout data in your home directory (`~/.strength_tracker/`). If no previous data exists, it will initialize with default Starting Strength starting weights.

## Project Structure

```
StrengthTracker/
├── strength_tracker/          # Software code
│   ├── __init__.py
│   └── strength_tracker.py   # Main application
├── config.yaml               # User configuration
├── requirements.txt           # Python dependencies
├── setup.py                  # Package setup
├── pyproject.toml            # Package configuration
├── PKGBUILD                  # AUR package build script
├── scripts/                  # Helper scripts
│   └── update-aur.sh        # AUR update script
└── ~/.strength_tracker/      # User data directory
    ├── workouts/             # Workout history
    ├── current_weights.yaml  # Current working weights
    └── failure_streaks.yaml  # Failure tracking
```

## Workout Program

Starting Strength follows a 3-day per week schedule:

- **Tuesday**: Week A or B workout
- **Thursday**: Week A or B workout  
- **Sunday**: Week A or B workout

### Week A Workout
1. **Squat** (3×5) - +2.5 kg per workout
2. **Bench Press** (3×5) - +2.5 kg per workout
3. **Deadlift** (1×5) - +5 kg per workout

### Week B Workout
1. **Squat** (3×5) - +2.5 kg per workout
2. **Overhead Press** (3×5) - +2.5 kg per workout
3. **Power Clean** (5×3) - +2.5 kg per workout

### Bonus Exercises (Every Week)
4. **Atlas Curl** (2×10) - Bodyweight
5. **Neck Curl** (3×15) - 5 kg starting weight
6. **Hanging Leg Raise** (3×10) - Bodyweight

## Configuration

The program uses a comprehensive YAML configuration system. You can customize your workout program by editing `config.yaml`:

```yaml
# Program Settings
program:
  name: "Starting Strength Program"
  schedule:
    days: [2, 4, 7]  # Tuesday, Thursday, Sunday

# Exercise Definitions
exercises:
  squat:
    starting_weight: 60
    progression: 2.5
    sets: 3
    reps: 5

# Workout Templates
workouts:
  week_A:
    - squat
    - bench_press
    - deadlift
    
  week_B:
    - squat
    - overhead_press
    - power_clean

# Bonus Exercises (repeat every week regardless of A/B cycle)
bonus_exercises:
  - atlas_curl
  - neck_curl
  - hanging_leg_raise

# Deload Settings
deload:
  stalling_attempts: 3
  reduce_percent: 10
```

## Analytics

The software tracks and displays:

- **Current Weights**: Per exercise with progress indicators
- **Workout History**: Complete session logs with dates and status
- **Progress Tracking**: Weight increases and deloads over time
- **Failure Streaks**: Consecutive failed sets per exercise
- **Session Details**: Sets, reps, weights, and completion status

## Context

This application implements Mark Rippetoe's Starting Strength program, designed for beginners to build strength quickly through consistent, progressive training with proper form. The program focuses on compound movements and linear progression, gradually increasing stress on the body until you can't, then managing deloads intelligently.

## Dependencies

- `click` (>=8.0.0) - Command line interface
- `rich` (>=10.0.0) - Beautiful terminal output
- `pyyaml` (>=6.0.0) - YAML file handling

## Development

This is a standalone application designed to be:
- **Self-contained**: All functionality in one file
- **Portable**: Can be moved to any directory
- **Simple**: Easy to understand and modify
- **Focused**: Does one thing well - Starting Strength tracking



## License

Free to use, modify, and distribute as you see fit.