
import os
import sys

# Allows the test file to import app.py
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from app import app, init_db


def setup_module():
    """Prepare the database before running tests."""
    init_db()


def test_dashboard_loads():
    """Test that the dashboard loads correctly."""
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"CampusGear" in response.data


def test_equipment_page_loads():
    """Test that the equipment page loads correctly."""
    client = app.test_client()

    response = client.get("/equipment")

    assert response.status_code == 200
    assert b"Equipment" in response.data


def test_search_equipment():
    """Test equipment search."""
    client = app.test_client()

    response = client.get("/equipment?search=Dell")

    assert response.status_code == 200
    assert b"Dell" in response.data


def test_category_filter():
    """Test the category filter."""
    client = app.test_client()

    response = client.get("/equipment?category=Laptop")

    assert response.status_code == 200


def test_condition_filter():
    """Test the condition filter."""
    client = app.test_client()

    response = client.get("/equipment?condition=Excellent")

    assert response.status_code == 200


def test_location_filter():
    """Test the location filter."""
    client = app.test_client()

    response = client.get("/equipment?location=Library")

    assert response.status_code == 200


def test_add_equipment_page_loads():
    """Test that the Add Equipment form loads."""
    client = app.test_client()

    response = client.get("/equipment/add")

    assert response.status_code == 200
    assert b"Equipment" in response.data


def test_invalid_page_returns_404():
    """Test that an invalid page returns a 404 error."""
    client = app.test_client()

    response = client.get("/this-page-does-not-exist")

    assert response.status_code == 404
