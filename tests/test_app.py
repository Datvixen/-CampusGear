import os
import sys

# Allow tests to import app.py from the project folder
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from app import app, init_db


def setup_module():
    """Prepare the database before running tests."""
    init_db()


def test_dashboard_loads():
    """Dashboard should load successfully."""
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"CampusGear" in response.data


def test_equipment_page_loads():
    """Equipment inventory page should load successfully."""
    client = app.test_client()

    response = client.get("/equipment")

    assert response.status_code == 200
    assert b"Equipment" in response.data


def test_search_equipment():
    """Search should return matching equipment."""
    client = app.test_client()

    response = client.get("/equipment?search=Dell")

    assert response.status_code == 200
    assert b"Dell" in response.data


def test_category_filter():
    """Category filter should load filtered results."""
    client = app.test_client()

    response = client.get("/equipment?category=Laptop")

    assert response.status_code == 200


def test_condition_filter():
    """Condition filter should work without an error."""
    client = app.test_client()

    response = client.get("/equipment?condition=Excellent")

    assert response.status_code == 200


def test_location_filter():
    """Location filter should work without an error."""
    client = app.test_client()

    response = client.get("/equipment?location=Library")

    assert response.status_code == 200


def test_add_equipment_page_loads():
    """Add Equipment form should load."""
    client = app.test_client()

    response = client.get("/equipment/add")

    assert response.status_code == 200
    assert b"Equipment" in response.data


def test_invalid_page_returns_404():
    """An invalid URL should return a 404 error."""
    client = app.test_client()

    response = client.get("/this-page-does-not-exist")

    assert response.status_code == 404
