from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

DEFAULT_ACTIVITIES = deepcopy(activities)
client = TestClient(app)


def reset_activities() -> None:
    activities.clear()
    activities.update(deepcopy(DEFAULT_ACTIVITIES))


@pytest.fixture(autouse=True)
def restore_activities() -> None:
    reset_activities()
    yield
    reset_activities()


def test_get_activities_returns_all_activities() -> None:
    # Arrange
    expected_activities = deepcopy(DEFAULT_ACTIVITIES)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_for_activity_adds_new_participant() -> None:
    # Arrange
    activity_name = "Chess Club"
    new_email = "test.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_missing_activity_returns_404() -> None:
    # Arrange
    activity_name = "Nonexistent Club"
    email = "missing.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup_returns_400() -> None:
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"
    assert activities[activity_name]["participants"].count(existing_email) == 1


def test_remove_participant_successfully_removes_student() -> None:
    # Arrange
    activity_name = "Gym Class"
    participant_email = "olivia@mergington.edu"
    assert participant_email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": participant_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {participant_email} from {activity_name}"}
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_from_missing_activity_returns_404() -> None:
    # Arrange
    activity_name = "No Club"
    email = "absent.student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_missing_participant_returns_404() -> None:
    # Arrange
    activity_name = "Gym Class"
    email = "missing.student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
