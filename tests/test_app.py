import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities state between tests."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_adds_participant(client):
    email = "tester@mergington.edu"

    assert email not in activities["Chess Club"]["participants"]

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 200

    assert email in activities["Chess Club"]["participants"]
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    email = "dup@mergington.edu"

    response1 = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response1.status_code == 200

    response2 = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response2.status_code == 400


def test_delete_participant(client):
    email = "remove@mergington.edu"

    client.post("/activities/Chess%20Club/signup", params={"email": email})

    response = client.delete(
        "/activities/Chess%20Club/participants", params={"email": email}
    )
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]
