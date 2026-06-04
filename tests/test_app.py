from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the shared in-memory activity state before each test."""
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield


def test_get_activities_returns_activity_data():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert data[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities_response.json()[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    duplicate_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    delete_response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities_response.json()[activity_name]["participants"]


def test_delete_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missingstudent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_delete_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
