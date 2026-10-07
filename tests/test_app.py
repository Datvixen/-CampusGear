from app import app, init_db


# Set up the database before the tests run
init_db()


def test_dashboard():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200


def test_equipment_page():
    client = app.test_client()
    response = client.get("/equipment")

    assert response.status_code == 200


def test_search():
    client = app.test_client()
    response = client.get("/equipment?search=Dell")

    assert response.status_code == 200


def test_category_filter():
    client = app.test_client()
    response = client.get("/equipment?category=Laptop")

    assert response.status_code == 200


def test_condition_filter():
    client = app.test_client()
    response = client.get("/equipment?condition=Excellent")

    assert response.status_code == 200


def test_location_filter():
    client = app.test_client()
    response = client.get("/equipment?location=Library")

    assert response.status_code == 200


def test_add_equipment_page():
    client = app.test_client()
    response = client.get("/equipment/add")

    assert response.status_code == 200


def test_bad_page():
    client = app.test_client()
    response = client.get("/page-that-does-not-exist")

    assert response.status_code == 404
