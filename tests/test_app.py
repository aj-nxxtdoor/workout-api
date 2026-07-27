import pytest

from server.app import create_app
from server.extensions import db


@pytest.fixture
def client():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()


def test_create_and_list_workouts(client):
    resp = client.post("/workouts", json={"name": "Leg Day", "date": "2026-07-20"})
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "Leg Day"

    resp = client.get("/workouts")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_workout_requires_name(client):
    resp = client.post("/workouts", json={"date": "2026-07-20"})
    assert resp.status_code == 400
    assert "name" in resp.get_json()["errors"]


def test_workout_blank_name_rejected_by_model(client):
    resp = client.post("/workouts", json={"name": "   ", "date": "2026-07-20"})
    assert resp.status_code == 400


def test_create_exercise_invalid_category(client):
    resp = client.post("/exercises", json={"name": "Curl", "category": "not-a-category"})
    assert resp.status_code == 400
    assert "category" in resp.get_json()["errors"]


def test_create_duplicate_exercise_name_rejected(client):
    client.post("/exercises", json={"name": "Squat", "category": "strength"})
    resp = client.post("/exercises", json={"name": "Squat", "category": "strength"})
    assert resp.status_code == 400


def test_add_exercise_to_workout(client):
    workout = client.post("/workouts", json={"name": "Leg Day", "date": "2026-07-20"}).get_json()
    exercise = client.post(
        "/exercises", json={"name": "Squat", "category": "strength"}
    ).get_json()

    resp = client.post(
        f"/workouts/{workout['id']}/exercises",
        json={"exercise_id": exercise["id"], "sets": 4, "reps": 12},
    )
    assert resp.status_code == 201
    assert len(resp.get_json()["workout_exercises"]) == 1


def test_add_exercise_requires_sets_reps_or_duration(client):
    workout = client.post("/workouts", json={"name": "Leg Day", "date": "2026-07-20"}).get_json()
    exercise = client.post(
        "/exercises", json={"name": "Squat", "category": "strength"}
    ).get_json()

    resp = client.post(
        f"/workouts/{workout['id']}/exercises",
        json={"exercise_id": exercise["id"]},
    )
    assert resp.status_code == 400


def test_delete_workout(client):
    workout = client.post("/workouts", json={"name": "Leg Day", "date": "2026-07-20"}).get_json()
    resp = client.delete(f"/workouts/{workout['id']}")
    assert resp.status_code == 204
    assert client.get(f"/workouts/{workout['id']}").status_code == 404
