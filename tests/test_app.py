import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Capture initial activities for reset
initial_activities = activities.copy()


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    global activities
    activities.clear()
    activities.update(initial_activities)


@pytest.fixture
def client():
    """Provide a TestClient instance for the app."""
    return TestClient(app, follow_redirects=False)


def test_root_redirect(client):
    """Test GET / redirects to static index."""
    # Arrange: No special setup needed
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code == 302
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client, reset_activities):
    """Test GET /activities returns all activities."""
    # Arrange: Activities reset to initial state
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data == activities


def test_signup_success(client, reset_activities):
    """Test successful signup for an activity."""
    # Arrange: Valid activity and new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found(client, reset_activities):
    """Test signup for non-existent activity."""
    # Arrange: Invalid activity name
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up(client, reset_activities):
    """Test signup when student is already registered."""
    # Arrange: Use an existing participant
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_delete_success(client, reset_activities):
    """Test successful unregister from an activity."""
    # Arrange: Use an existing participant
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert email not in activities[activity_name]["participants"]


def test_delete_activity_not_found(client, reset_activities):
    """Test unregister from non-existent activity."""
    # Arrange: Invalid activity name
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_delete_not_signed_up(client, reset_activities):
    """Test unregister when student is not signed up."""
    # Arrange: Valid activity, but email not in participants
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]