from flask import Flask, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from server.config import Config
from server.extensions import db, migrate
from server.models import Workout, Exercise, WorkoutExercise
from server.schemas import (
    workout_schema,
    workouts_schema,
    exercise_schema,
    exercises_schema,
    workout_exercise_schema,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    register_routes(app)
    register_error_handlers(app)

    return app


def register_routes(app):
    # ------------------------------------------------------------------ #
    # Workouts
    # ------------------------------------------------------------------ #
    @app.get("/workouts")
    def get_workouts():
        workouts = Workout.query.all()
        return jsonify(workouts_schema.dump(workouts)), 200

    @app.get("/workouts/<int:id>")
    def get_workout(id):
        workout = Workout.query.get(id)
        if workout is None:
            return jsonify({"error": "Workout not found"}), 404
        return jsonify(workout_schema.dump(workout)), 200

    @app.post("/workouts")
    def create_workout():
        data = workout_schema.load(request.get_json() or {})
        workout = Workout(name=data["name"], date=data["date"], notes=data.get("notes"))
        db.session.add(workout)
        db.session.commit()
        return jsonify(workout_schema.dump(workout)), 201

    @app.delete("/workouts/<int:id>")
    def delete_workout(id):
        workout = Workout.query.get(id)
        if workout is None:
            return jsonify({"error": "Workout not found"}), 404
        db.session.delete(workout)
        db.session.commit()
        return "", 204

    # ------------------------------------------------------------------ #
    # Exercises
    # ------------------------------------------------------------------ #
    @app.get("/exercises")
    def get_exercises():
        exercises = Exercise.query.all()
        return jsonify(exercises_schema.dump(exercises)), 200

    @app.get("/exercises/<int:id>")
    def get_exercise(id):
        exercise = Exercise.query.get(id)
        if exercise is None:
            return jsonify({"error": "Exercise not found"}), 404
        return jsonify(exercise_schema.dump(exercise)), 200

    @app.post("/exercises")
    def create_exercise():
        data = exercise_schema.load(request.get_json() or {})
        exercise = Exercise(
            name=data["name"],
            category=data["category"],
            equipment_needed=data.get("equipment_needed", False),
        )
        db.session.add(exercise)
        db.session.commit()
        return jsonify(exercise_schema.dump(exercise)), 201

    @app.delete("/exercises/<int:id>")
    def delete_exercise(id):
        exercise = Exercise.query.get(id)
        if exercise is None:
            return jsonify({"error": "Exercise not found"}), 404
        db.session.delete(exercise)
        db.session.commit()
        return "", 204

    # ------------------------------------------------------------------ #
    # Adding an exercise to a workout
    # ------------------------------------------------------------------ #
    @app.post("/workouts/<int:id>/exercises")
    def add_exercise_to_workout(id):
        workout = Workout.query.get(id)
        if workout is None:
            return jsonify({"error": "Workout not found"}), 404

        data = workout_exercise_schema.load(request.get_json() or {})

        exercise = Exercise.query.get(data["exercise_id"])
        if exercise is None:
            return jsonify({"error": "Exercise not found"}), 404

        workout_exercise = WorkoutExercise(
            workout_id=workout.id,
            exercise_id=exercise.id,
            sets=data.get("sets"),
            reps=data.get("reps"),
            duration_seconds=data.get("duration_seconds"),
        )
        db.session.add(workout_exercise)
        db.session.commit()
        return jsonify(workout_schema.dump(workout)), 201


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({"errors": err.messages}), 400

    @app.errorhandler(ValueError)
    def handle_value_error(err):
        db.session.rollback()
        return jsonify({"error": str(err)}), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err):
        db.session.rollback()
        return jsonify({"error": "Database constraint violated.", "detail": str(err.orig)}), 400


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
