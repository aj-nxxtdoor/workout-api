from datetime import date

from server.app import create_app
from server.extensions import db
from server.models import Workout, Exercise, WorkoutExercise

app = create_app()

with app.app_context():
    print("Clearing existing data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print("Seeding exercises...")
    push_up = Exercise(name="Push-Up", category="strength", equipment_needed=False)
    squat = Exercise(name="Squat", category="strength", equipment_needed=False)
    running = Exercise(name="Running", category="cardio", equipment_needed=False)
    plank = Exercise(name="Plank", category="strength", equipment_needed=False)
    hamstring_stretch = Exercise(
        name="Hamstring Stretch", category="flexibility", equipment_needed=False
    )
    single_leg_stand = Exercise(
        name="Single-Leg Stand", category="balance", equipment_needed=False
    )

    db.session.add_all(
        [push_up, squat, running, plank, hamstring_stretch, single_leg_stand]
    )
    db.session.commit()

    print("Seeding workouts...")
    leg_day = Workout(name="Leg Day", date=date(2026, 7, 20), notes="Focus on form")
    full_body = Workout(name="Full Body Blast", date=date(2026, 7, 22))
    recovery = Workout(name="Active Recovery", date=date(2026, 7, 24), notes="Light session")

    db.session.add_all([leg_day, full_body, recovery])
    db.session.commit()

    print("Linking exercises to workouts...")
    db.session.add_all(
        [
            WorkoutExercise(workout_id=leg_day.id, exercise_id=squat.id, sets=4, reps=12),
            WorkoutExercise(
                workout_id=leg_day.id, exercise_id=single_leg_stand.id, duration_seconds=60
            ),
            WorkoutExercise(workout_id=full_body.id, exercise_id=push_up.id, sets=3, reps=15),
            WorkoutExercise(workout_id=full_body.id, exercise_id=squat.id, sets=3, reps=10),
            WorkoutExercise(
                workout_id=full_body.id, exercise_id=running.id, duration_seconds=900
            ),
            WorkoutExercise(workout_id=recovery.id, exercise_id=plank.id, sets=2, reps=1),
            WorkoutExercise(
                workout_id=recovery.id,
                exercise_id=hamstring_stretch.id,
                duration_seconds=120,
            ),
        ]
    )
    db.session.commit()

    print("Done seeding!")
