# Workout Tracker API

## Description

A Flask + SQLAlchemy + Marshmallow backend API for a workout tracking
application used by personal trainers. The API supports creating, viewing,
and deleting **Workouts** and **Exercises**, and adding a reusable Exercise
to a Workout with per-workout details (sets/reps, or a duration).

**Entities**

- **Workout** — a training session (`name`, `date`, optional `notes`).
- **Exercise** — a reusable movement (`name`, `category`, `equipment_needed`).
- **WorkoutExercise** — the join between a Workout and an Exercise, holding
  the `sets`, `reps`, and/or `duration_seconds` for that exercise within
  that specific workout.

A Workout has many Exercises through WorkoutExercise, and an Exercise can
belong to many Workouts through WorkoutExercise (many-to-many with extra
data on the join table).

## Installation

1. Clone the repo and move into it:
   ```bash
   git clone <your-repo-url>
   cd workout-api
   ```
2. Install dependencies with Pipenv:
   ```bash
   pipenv install
   pipenv shell
   ```
3. Set the Flask app environment variable:
   ```bash
   export FLASK_APP=server.app
   ```
4. Run the database migrations:
   ```bash
   flask db upgrade
   ```
5. Seed the database with example data:
   ```bash
   python3 -m server.seed
   ```

## Running the App

```bash
flask run --port 5555
```

The API will be available at `http://127.0.0.1:5555`.

## Running Tests

```bash
python3 -m pytest tests/
```

## Endpoints

### Workouts

| Method | Route | Description |
|---|---|---|
| GET | `/workouts` | List all workouts, including their linked exercises. |
| GET | `/workouts/<id>` | View a single workout, including its linked exercises. |
| POST | `/workouts` | Create a workout. Body: `{ "name": str, "date": "YYYY-MM-DD", "notes": str (optional) }` |
| DELETE | `/workouts/<id>` | Delete a workout (and its workout-exercise links). |

### Exercises

| Method | Route | Description |
|---|---|---|
| GET | `/exercises` | List all exercises. |
| GET | `/exercises/<id>` | View a single exercise. |
| POST | `/exercises` | Create an exercise. Body: `{ "name": str, "category": "cardio"\|"strength"\|"flexibility"\|"balance", "equipment_needed": bool (optional) }` |
| DELETE | `/exercises/<id>` | Delete an exercise (and any workout links using it). |

### Adding an Exercise to a Workout

| Method | Route | Description |
|---|---|---|
| POST | `/workouts/<id>/exercises` | Attach an existing exercise to the workout. Body: `{ "exercise_id": int, "sets": int (optional), "reps": int (optional), "duration_seconds": int (optional) }`. Either `sets`/`reps` or `duration_seconds` must be supplied. Returns the updated workout with its full list of exercises. |

## Validations

- **Table constraints:** non-blank workout name, unique exercise name,
  non-blank exercise category, positive `sets`/`reps`/`duration_seconds`.
- **Model validations:** blank-name checks on Workout/Exercise, allowed
  category list on Exercise, positive-number checks on WorkoutExercise.
- **Schema validations:** required/length checks on Workout and Exercise
  fields, `OneOf` category check, `Range` checks on numeric
  WorkoutExercise fields, and a cross-field check requiring either
  sets/reps or a duration.

## Project Structure

server/ - the actual Flask app
  app.py        -> routes + error handling
  config.py     -> db config
  extensions.py -> db/migrate setup
  models.py     -> Workout, Exercise, 
  WorkoutExercise + validations
  schemas.py    -> marshmallow schemas + validations
  seed.py       -> fills the db with sample data

migrations/  -> flask-migrate files, don't touch by hand
tests/       -> pytest tests
Pipfile      -> dependencies
README.md    -> this file
