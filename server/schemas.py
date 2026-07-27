from marshmallow import Schema, fields, validate, validates_schema, ValidationError

from server.models import ALLOWED_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    # Schema validation #1: name is required and must be 1-100 characters.
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    # Schema validation #2: category is required and restricted to a fixed set.
    category = fields.String(
        required=True, validate=validate.OneOf(ALLOWED_CATEGORIES)
    )
    equipment_needed = fields.Boolean(load_default=False)


class WorkoutExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    workout_id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(required=True)

    # Schema validation #3/#4/#5: numeric fields, when supplied, must be > 0.
    sets = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    reps = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    duration_seconds = fields.Integer(allow_none=True, validate=validate.Range(min=1))

    # Nested exercise details, included on read so the client doesn't have
    # to make a second request to know which exercise this row refers to.
    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    @validates_schema
    def validate_has_sets_reps_or_duration(self, data, **kwargs):
        has_sets_or_reps = data.get("sets") is not None or data.get("reps") is not None
        has_duration = data.get("duration_seconds") is not None
        if not has_sets_or_reps and not has_duration:
            raise ValidationError(
                "Provide either sets/reps or a duration_seconds value.",
                field_name="_schema",
            )


class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)
    # Schema validation #6: name is required and must be 1-100 characters.
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    # Schema validation #7: date is required and must parse to a real date.
    date = fields.Date(required=True)
    notes = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))

    workout_exercises = fields.Nested(
        WorkoutExerciseSchema, many=True, dump_only=True
    )


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()
