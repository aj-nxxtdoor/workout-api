from datetime import date as date_cls

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

from server.extensions import db

# Allowed categories for an Exercise. Used by both the model validation
# below and the Marshmallow schema validation, so trainers can't create
# an exercise with a made-up category.
ALLOWED_CATEGORIES = ["cardio", "strength", "flexibility", "balance"]


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date_cls.today)
    notes = db.Column(db.String(500))

    # Association-object relationship: a Workout has many WorkoutExercise
    # rows, each of which points at one Exercise. cascade="all, delete-orphan"
    # means deleting a Workout also removes its WorkoutExercise rows
    # (but NOT the Exercise records themselves, since those are reusable).
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )

    # Convenience read-only view of the exercises attached to this workout,
    # going through the workout_exercises association.
    exercises = association_proxy("workout_exercises", "exercise")

    __table_args__ = (
        # Table constraint #1: a workout must have a non-blank name.
        CheckConstraint("length(trim(name)) > 0", name="ck_workout_name_not_blank"),
    )

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Workout name cannot be blank.")
        return value.strip()

    @validates("date")
    def validate_date(self, key, value):
        if value is None:
            raise ValueError("Workout date is required.")
        return value

    def __repr__(self):
        return f"<Workout {self.id} {self.name}>"


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )

    workouts = association_proxy("workout_exercises", "workout")

    __table_args__ = (
        # Table constraint #2: exercise names must be unique so the same
        # movement isn't duplicated under slightly different rows.
        UniqueConstraint("name", name="uq_exercise_name"),
        # Table constraint #3: category can never be blank at the DB level.
        CheckConstraint("length(trim(category)) > 0", name="ck_exercise_category_not_blank"),
    )

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name cannot be blank.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        if not value or value.lower() not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Category must be one of: {', '.join(ALLOWED_CATEGORIES)}."
            )
        return value.lower()

    def __repr__(self):
        return f"<Exercise {self.id} {self.name}>"


class WorkoutExercise(db.Model):
    """Association object linking a Workout to an Exercise, carrying the
    per-workout details (sets/reps or duration) for that exercise.
    """

    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)

    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    __table_args__ = (
        # Table constraint #4: sets, if provided, must be positive.
        CheckConstraint("sets IS NULL OR sets > 0", name="ck_workout_exercise_sets_positive"),
        # Table constraint #5: reps, if provided, must be positive.
        CheckConstraint("reps IS NULL OR reps > 0", name="ck_workout_exercise_reps_positive"),
        # Table constraint #6: duration, if provided, must be positive.
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_workout_exercise_duration_positive",
        ),
    )

    @validates("sets", "reps", "duration_seconds")
    def validate_positive(self, key, value):
        if value is not None and value <= 0:
            raise ValueError(f"{key} must be a positive number.")
        return value

    def __repr__(self):
        return f"<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id}>"
