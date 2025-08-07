#!/usr/bin/env python3
"""
StrengthTracker - A simple workout tracking app for Starting Strength.
"""

import yaml
import click
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from typing import Dict, List
import sys

console = Console()

class StrengthTracker:
    def __init__(self):
        # Use user's home directory for data storage
        self.data_dir = Path.home() / ".strength_tracker"
        self.data_dir.mkdir(exist_ok=True)
        self.workouts_dir = self.data_dir / "workouts"
        self.workouts_dir.mkdir(exist_ok=True)
        
        # Load program configuration
        self.program = self.load_program()
        self.current_weights = self.load_weights()
        self.failure_streaks = self.load_failure_streaks()
        
    def load_program(self) -> Dict:
        """Load the Starting Strength program configuration from config.yaml."""
        config_file = Path("config.yaml")
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = yaml.safe_load(f)
                
                # Merge config sections into program structure
                program = {
                    "name": config.get("program", {}).get("name", "Starting Strength Program"),
                    "description": config.get("program", {}).get("description", "Classic Starting Strength linear progression"),
                    "schedule": config.get("program", {}).get("schedule", {"days": [2, 4, 7]}),
                    "cycle": config.get("program", {}).get("cycle", ["week_A", "week_B"]),
                                    "exercises": config.get("exercises", {}),
                "workouts": config.get("workouts", {}),
                "bonus_exercises": config.get("bonus_exercises", []),
                "deload": config.get("deload", {"stalling_attempts": 3, "reduce_percent": 10}),
                "rounding": config.get("rounding", {"increment": 2.5, "unit": "kg"})
                }
                
                return program
                
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load config.yaml: {e}[/yellow]")
                console.print("[yellow]Using default configuration.[/yellow]")
        
        # Fallback to default configuration
        return {
            "name": "Starting Strength Program",
            "description": "Classic Starting Strength linear progression",
            "schedule": {
                "days": [2, 4, 7]  # Tue/Thu/Sun
            },
            "cycle": ["week_A", "week_B"],
            "exercises": {
                "squat": {
                    "starting_weight": 60,
                    "progression": 2.5,
                    "sets": 3,
                    "reps": 5
                },
                "bench_press": {
                    "starting_weight": 50,
                    "progression": 2.5,
                    "sets": 3,
                    "reps": 5
                },
                "overhead_press": {
                    "starting_weight": 40,
                    "progression": 2.5,
                    "sets": 3,
                    "reps": 5
                },
                "deadlift": {
                    "starting_weight": 80,
                    "progression": 5,
                    "sets": 1,
                    "reps": 5
                },
                "power_clean": {
                    "starting_weight": 40,
                    "progression": 2.5,
                    "sets": 5,
                    "reps": 3
                },
                "atlas_curl": {
                    "starting_weight": "bodyweight",
                    "progression": 0,
                    "sets": 2,
                    "reps": 10,
                    "no_warmup": True
                },
                "neck_curl": {
                    "starting_weight": 5,
                    "progression": 1,
                    "sets": 3,
                    "reps": 15,
                    "no_warmup": True
                },
                "hanging_leg_raise": {
                    "starting_weight": "bodyweight",
                    "progression": 0,
                    "sets": 3,
                    "reps": 10,
                    "no_warmup": True
                }
            },
            "workouts": {
                "week_A": ["squat", "bench_press", "deadlift"],
                "week_B": ["squat", "overhead_press", "power_clean"]
            },
            "bonus_exercises": ["atlas_curl", "neck_curl", "hanging_leg_raise"],
            "deload": {"stalling_attempts": 3, "reduce_percent": 10},
            "rounding": {"increment": 2.5, "unit": "kg"}
        }
    
    def load_weights(self) -> Dict:
        """Load current weights from file or initialize defaults."""
        weights_file = self.data_dir / "current_weights.yaml"
        
        if weights_file.exists():
            try:
                with open(weights_file) as f:
                    return yaml.safe_load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load weights file: {e}[/yellow]")
        
        # Initialize with starting weights
        weights = {}
        for exercise, config in self.program["exercises"].items():
            weights[exercise] = config["starting_weight"]
        
        self.save_weights(weights)
        return weights
    
    def load_failure_streaks(self) -> Dict:
        """Load failure streaks from file or initialize defaults."""
        streaks_file = self.data_dir / "failure_streaks.yaml"
        
        if streaks_file.exists():
            try:
                with open(streaks_file) as f:
                    return yaml.safe_load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load failure streaks file: {e}[/yellow]")
        
        # Initialize with empty streaks
        streaks = {}
        for exercise in self.program["exercises"].keys():
            streaks[exercise] = 0
        
        self.save_failure_streaks(streaks)
        return streaks
    
    def save_failure_streaks(self, streaks: Dict):
        """Save failure streaks to file."""
        streaks_file = self.data_dir / "failure_streaks.yaml"
        try:
            with open(streaks_file, 'w') as f:
                yaml.dump(streaks, f)
        except Exception as e:
            console.print(f"[red]Error saving failure streaks: {e}[/red]")
    
    def round_weight(self, weight: float) -> float:
        """Round weight to nearest increment (default 2.5 kg)."""
        if weight == "bodyweight":
            return weight
        increment = self.program.get("rounding", {}).get("increment", 2.5)
        return round(weight / increment) * increment
    
    def save_weights(self, weights: Dict):
        """Save current weights to file."""
        weights_file = self.data_dir / "current_weights.yaml"
        try:
            with open(weights_file, 'w') as f:
                yaml.dump(weights, f)
        except Exception as e:
            console.print(f"[red]Error saving weights: {e}[/red]")
    
    def get_current_workout(self) -> str:
        """Determine which workout is due today."""
        today = datetime.now()
        # Use a rolling 2-week cycle based on current date
        # This avoids the hardcoded 2024 issue
        days_since_epoch = (today - datetime(1970, 1, 1)).days
        week_number = days_since_epoch // 7
        
        # Alternate between week A and B
        return "week_A" if week_number % 2 == 0 else "week_B"
    

    
    def get_workout_status(self) -> Dict:
        """Get workout status for today and this week."""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # Check if worked out today
        today_file = self.workouts_dir / f"{today.strftime('%Y_%m_%d')}.yaml"
        worked_out_today = today_file.exists()
        
        # Check if worked out yesterday
        yesterday_file = self.workouts_dir / f"{yesterday.strftime('%Y_%m_%d')}.yaml"
        worked_out_yesterday = yesterday_file.exists()
        
        # Count workouts this week
        week_start = today - timedelta(days=today.weekday())
        week_workouts = 0
        for i in range(7):
            check_date = week_start + timedelta(days=i)
            if check_date <= today:
                check_file = self.workouts_dir / f"{check_date.strftime('%Y_%m_%d')}.yaml"
                if check_file.exists():
                    week_workouts += 1
        
        return {
            "worked_out_today": worked_out_today,
            "worked_out_yesterday": worked_out_yesterday,
            "week_workouts": week_workouts
        }
    
    def get_warmup_sets(self, exercise: str, working_weight: float) -> List[Dict]:
        """Calculate warmup sets for an exercise."""
        exercise_config = self.program["exercises"][exercise]
        
        # No warmups for bodyweight exercises or exercises marked as no_warmup
        if working_weight == "bodyweight" or exercise_config.get("no_warmup", False):
            return []
        
        warmup_sets = []
        percentages = [50, 70, 90]
        reps = [5, 3, 1]
        
        for percent, rep in zip(percentages, reps):
            warmup_weight = int(working_weight * percent / 100)
            warmup_sets.append({
                "weight": warmup_weight,
                "reps": rep,
                "type": "warmup"
            })
        
        return warmup_sets
    
    def start_workout(self):
        """Start a workout session."""
        console.clear()
        console.print(Panel.fit(
            "[bold blue]StrengthTracker[/bold blue]\n"
            "Starting Strength Program"
        ))
        
        # Get workout status
        status = self.get_workout_status()
        
        # Check if already worked out today
        if status["worked_out_today"]:
            console.print("[red]You have already worked out today. Rest is important.[/red]")
            return
        
        # Check if worked out yesterday (rest day warning)
        if status["worked_out_yesterday"]:
            console.print("[yellow]You worked out yesterday. One rest day is recommended.[/yellow]")
            if not Confirm.ask("Are you sure you want to workout today?"):
                return
        
        # Check weekly limit (just warn, do not block)
        if status["week_workouts"] >= 3:
            console.print(f"[yellow]You have already completed {status['week_workouts']} workouts this week.[/yellow]")
            if not Confirm.ask("Are you sure you want to continue?"):
                return
        
        current_workout = self.get_current_workout()
        exercises = self.program["workouts"][current_workout] + self.program["bonus_exercises"]
        
        console.print(f"\n[bold]Today's workout: {current_workout}[/bold]")
        console.print(f"[dim]Exercises: {', '.join(exercises)}[/dim]\n")
        
        console.print("[bold blue]Instructions:[/bold blue]")
        console.print("• For each set, you must type:")
        console.print("  - 'w' or 'win' to mark as successful")
        console.print("  - 'f' or 'fail' to mark as failed")
        console.print("  - 'q' or 'quit' to quit the workout")
        console.print("• You can also type a number for custom reps\n")
        

        
        # Track workout
        today = datetime.now()
        filename = f"{today.strftime('%Y_%m_%d')}.yaml"
        filepath = self.workouts_dir / filename
        
        workout_data = {
            "date": today.strftime('%Y-%m-%d'),
            "time": today.strftime('%H:%M:%S'),
            "workout": current_workout,
            "exercises": {}
        }
        
        # Go through each exercise
        for exercise in exercises:
            console.print(f"\n[bold]{exercise.replace('_', ' ').title()}[/bold]")
            
            exercise_config = self.program["exercises"][exercise]
            current_weight = self.current_weights[exercise]
            
            # Show current weight
            if current_weight == "bodyweight":
                console.print(f"Current: Bodyweight")
            else:
                console.print(f"Current weight: {current_weight} kg")
            
            # Calculate warmup sets
            if not exercise_config.get("no_warmup", False):
                warmup_sets = self.get_warmup_sets(exercise, current_weight)
                console.print("\nWarmup sets:")
                for i, set_data in enumerate(warmup_sets, 1):
                    console.print(f"  {i}. {set_data['weight']} kg × {set_data['reps']}")
            
            # Working sets
            sets = exercise_config["sets"]
            reps = exercise_config["reps"]
            console.print(f"\nWorking sets: {sets} × {reps}")
            
            # Track performance
            exercise_data = {
                "weight": current_weight,
                "sets": [],
                "completed": True
            }
            
            # Record each set
            for set_num in range(sets):
                console.print(f"\nSet {set_num + 1}:")
                
                # Use the current weight automatically
                weight_input = current_weight
                
                while True:
                    reps_input = Prompt.ask(f"Set {set_num + 1} - Reps completed")
                    if reps_input.lower() in ["q", "quit"]:
                        return
                    if reps_input.lower() in ["f", "fail"]:
                        reps_completed = 0  # Mark as failed
                        break
                    elif reps_input.lower() in ["w", "win"]:
                        reps_completed = reps  # Mark as successful
                        break
                    elif reps_input.strip() == "":  # Empty input
                        console.print("[red]Please type 'w' for success, 'f' for fail, or a number.[/red]")
                        continue
                    else:
                        try:
                            reps_completed = int(reps_input)
                            break
                        except ValueError:
                            console.print("[red]Invalid input. Please type 'w' for success, 'f' for fail, or a number.[/red]")
                            continue
                
                # Check if failed
                failed = reps_completed < reps
                
                set_data = {
                    "set": set_num + 1,
                    "weight": weight_input,
                    "target_reps": reps,
                    "actual_reps": reps_completed,
                    "failed": failed
                }
                
                exercise_data["sets"].append(set_data)
                
                if failed:
                    console.print(f"[red]Failed set ({reps_completed}/{reps} reps)[/red]")
                    self.failure_streaks[exercise] += 1
                    
                    # Check if deload is needed (configurable consecutive failures)
                    stalling_attempts = self.program.get("deload", {}).get("stalling_attempts", 3)
                    if self.failure_streaks[exercise] >= stalling_attempts:
                        if current_weight != "bodyweight":
                            reduce_percent = self.program.get("deload", {}).get("reduce_percent", 10)
                            new_weight = self.round_weight(current_weight * (1 - reduce_percent / 100))
                            self.current_weights[exercise] = new_weight
                            self.failure_streaks[exercise] = 0  # Reset streak
                            console.print(f"[yellow]Automatic deload: Weight reduced to {new_weight} kg[/yellow]")
                            console.print("[yellow]This is a deloaded set.[/yellow]")
                        else:
                            console.print("[yellow]Deload not applicable for bodyweight exercise.[/yellow]")
                    else:
                        console.print(f"[yellow]Failure streak: {self.failure_streaks[exercise]}/{stalling_attempts}[/yellow]")
                else:
                    console.print(f"[green]Good set ({reps_completed}/{reps} reps)[/green]")
                    # Reset failure streak on success
                    if self.failure_streaks[exercise] > 0:
                        self.failure_streaks[exercise] = 0
                        console.print("[green]Failure streak reset.[/green]")
            
            # Automatically increase weight if all sets successful
            if not any(set_data["failed"] for set_data in exercise_data["sets"]):
                if exercise_config["progression"] > 0 and current_weight != "bodyweight":
                    new_weight = self.round_weight(current_weight + exercise_config["progression"])
                    self.current_weights[exercise] = new_weight
                    console.print(f"[green]Weight increased to {new_weight} kg[/green]")
            
            workout_data["exercises"][exercise] = exercise_data
        
        # Save workout
        with open(filepath, 'w') as f:
            yaml.dump(workout_data, f)
        
        # Save updated weights and failure streaks
        self.save_weights(self.current_weights)
        self.save_failure_streaks(self.failure_streaks)
        
        console.print(f"\n[green]Workout saved to {filepath}[/green]")
    
    def view_history(self):
        """View workout history."""
        console.clear()
        console.print("[bold]Workout History[/bold]\n")
        
        entries = list(self.workouts_dir.glob("*.yaml"))
        if not entries:
            console.print("[yellow]No workout entries found.[/yellow]")
            return
        
        # Sort by date
        entries.sort(reverse=True)
        
        table = Table()
        table.add_column("Date")
        table.add_column("Workout")
        table.add_column("Exercises")
        table.add_column("Status")
        
        for entry_file in entries[:20]:  # Show last 20 entries
            try:
                with open(entry_file) as f:
                    entry = yaml.safe_load(f)
                
                date = entry.get('date', 'Unknown')
                workout = entry.get('workout', 'Unknown')
                exercises = list(entry.get('exercises', {}).keys())
                exercise_count = len(exercises)
                
                # Check if all exercises completed
                all_completed = all(
                    ex_data.get('completed', False) 
                    for ex_data in entry.get('exercises', {}).values()
                )
                status = "✓" if all_completed else "✗"
                
                table.add_row(date, workout, f"{exercise_count} exercises", status)
                
            except Exception as e:
                console.print(f"[red]Error reading {entry_file}: {e}[/red]")
        
        console.print(table)
    
    def view_progress(self):
        """View comprehensive analytics and progress."""
        console.clear()
        console.print("[bold]StrengthTracker Analytics[/bold]\n")
        
        # Get all workout files
        workout_files = list(self.workouts_dir.glob("*.yaml"))
        
        if not workout_files:
            console.print("[yellow]No workout data found.[/yellow]")
            return
        
        # Calculate analytics
        total_workouts = len(workout_files)
        total_weight_moved = {}
        total_time_spent = 0
        first_workout_date = None
        last_workout_date = None
        
        # Base exercises (not bonus)
        base_exercises = ["squat", "bench_press", "overhead_press", "deadlift", "power_clean"]
        
        for workout_file in workout_files:
            try:
                with open(workout_file) as f:
                    workout = yaml.safe_load(f)
                
                date = workout.get('date')
                if date:
                    if first_workout_date is None:
                        first_workout_date = date
                    last_workout_date = date
                
                # Calculate weight moved for base exercises
                for exercise, ex_data in workout.get('exercises', {}).items():
                    if exercise in base_exercises:
                        weight = ex_data.get('weight', 0)
                        if weight != "bodyweight" and isinstance(weight, (int, float)):
                            sets = ex_data.get('sets', [])
                            for set_data in sets:
                                reps = set_data.get('actual_reps', 0)
                                if reps > 0:
                                    total_weight_moved[exercise] = total_weight_moved.get(exercise, 0) + (weight * reps)
                
            except Exception as e:
                console.print(f"[red]Error reading {workout_file}: {e}[/red]")
        
        # Display analytics
        console.print(f"[bold]Total Workouts:[/bold] {total_workouts}")
        
        if first_workout_date and last_workout_date:
            from datetime import datetime
            start_date = datetime.strptime(first_workout_date, '%Y-%m-%d')
            end_date = datetime.strptime(last_workout_date, '%Y-%m-%d')
            days_on_program = (end_date - start_date).days
            console.print(f"[bold]Days on Program:[/bold] {days_on_program}")
            console.print(f"[bold]Started:[/bold] {first_workout_date}")
            console.print(f"[bold]Last Workout:[/bold] {last_workout_date}")
        
        console.print(f"\n[bold]Total Weight Moved (Base Exercises):[/bold]")
        for exercise in base_exercises:
            if exercise in total_weight_moved:
                weight_moved = total_weight_moved[exercise]
                console.print(f"  {exercise.replace('_', ' ').title()}: {weight_moved:,.0f} kg")
        
        console.print(f"\n[bold]Current Weights:[/bold]")
        table = Table()
        table.add_column("Exercise")
        table.add_column("Current Weight")
        table.add_column("Starting Weight")
        table.add_column("Progress")
        
        for exercise, config in self.program["exercises"].items():
            current = self.current_weights[exercise]
            starting = config["starting_weight"]
            
            if current == "bodyweight" or starting == "bodyweight":
                progress = "N/A"
            else:
                progress = f"+{current - starting} kg"
            
            table.add_row(
                exercise.replace('_', ' ').title(),
                str(current),
                str(starting),
                progress
            )
        
        console.print(table)
    
    def run(self):
        """Run the main application loop."""
        while True:
            console.clear()
            console.print(Panel.fit(
                "[bold blue]StrengthTracker[/bold blue]\n"
                "Starting Strength Program"
            ))
            
            console.print("\n[1] Start Workout")
            console.print("[2] View History")
            console.print("[3] View Progress")
            console.print("[q] Quit\n")
            
            choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "q"])
            
            if choice == "1":
                self.start_workout()
                Prompt.ask("\nPress Enter to continue...")
            elif choice == "2":
                self.view_history()
                Prompt.ask("\nPress Enter to continue...")
            elif choice == "3":
                self.view_progress()
                Prompt.ask("\nPress Enter to continue...")
            elif choice == "q":
                break

@click.command()
def main():
    """Run the StrengthTracker application."""
    # Check dependencies
    try:
        import click
        import rich
        import yaml
    except ImportError as e:
        console.print(f"[red bold]Error:[/red bold] Missing required dependency: {e}")
        console.print("Please install dependencies with: pip install click rich pyyaml")
        sys.exit(1)
    
    try:
        StrengthTracker().run()
    except KeyboardInterrupt:
        console.print("\n[green]Goodbye.[/green]")
    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {str(e)}")
        console.print("\nIf this is a data corruption issue, try deleting the .strength_tracker directory in your home folder.")

if __name__ == '__main__':
    main() 