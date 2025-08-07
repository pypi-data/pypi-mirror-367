# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Initial release of StrengthTracker
- Starting Strength program implementation
- Automatic workout scheduling (Week A/B rotation)
- Weight progression tracking
- Deload management for failed sets
- Warmup set calculations
- Workout history tracking
- Progress visualization
- Local YAML data storage
- Terminal-based user interface using Rich library

### Features
- **Workout Management**: Track Starting Strength workouts with automatic progression
- **Weight Progression**: +2.5 kg for most lifts, +5 kg for deadlift
- **Deload Logic**: 10% weight reduction on failed sets
- **Warmup Sets**: Automatic calculation of warmup sets (50%, 70%, 90%)
- **Data Persistence**: All data stored in human-readable YAML format
- **Progress Tracking**: View current weights and workout history
- **Schedule Enforcement**: Tuesday, Thursday, Sunday workout days

### Technical
- Python 3.8+ compatibility
- Rich terminal interface
- Click command-line framework
- PyYAML for data storage
- Standalone application design
