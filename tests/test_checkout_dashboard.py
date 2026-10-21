from datetime import date, timedelta
from html import unescape
import re

import app as campusgear
import pytest


def iso_date(days_from_today=0):
    return (date.today() + timedelta(days=days_from_today)).isoformat()


def valid_checkout_form(**overrides):
    form = {
        "equipment_id": "1",
        "borrower_name": "Campus Borrower",
        "borrower_email": "borrower@example.edu",
        "quantity": "2",
        "checkout_date": iso_date(),
        "due_date": iso_date(7),
    }
    form.update(overrides)
    return form


def insert_checkout(
    equipment_id=1,
    borrower_name="Test Borrower",
    borrower_email="test@example.edu",
    quantity=1,
    checkout_date=None,
    due_date=None,
    return_date=None,
    status="Checked Out",
):
    connection = campusgear.db()
    cursor = connection.execute(
        "INSERT INTO checkouts(equipment_id,borrower_name,borrower_email,quantity,checkout_date,due_date,return_date,status) "
        "VALUES(?,?,?,?,?,?,?,?)",
        (
            equipment_id,
            borrower_name,
            borrower_email,
            quantity,
            checkout_date or iso_date(-1),
            due_date or iso_date(7),
            return_date,
            status,
        ),
    )
    connection.commit()
    checkout_id = cursor.lastrowid
    connection.close()
    return checkout_id


def checkout_rows():
    connection = campusgear.db()
    rows = connection.execute("SELECT * FROM checkouts ORDER BY id").fetchall()
    connection.close()
    return rows


def inventory_row(response, asset_tag):
    page = response.get_data(as_text=True)
    for row in re.findall(r"<tr>\s*(.*?)\s*</tr>", page, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        values = [
            " ".join(unescape(re.sub(r"<[^>]+>", " ", cell)).split())
            for cell in cells
        ]
        if values and values[0] == asset_tag:
            return values
    raise AssertionError(f"No equipment row found for {asset_tag}")


def dashboard_stat(response, label):
    pattern = rf"<h3>\s*{re.escape(label)}\s*</h3>\s*<p class=\"stat-number\">(\d+)"
    match = re.search(pattern, response.get_data(as_text=True))
    assert match is not None, f"Dashboard statistic {label!r} was not rendered"
    return int(match.group(1))


def test_checkout_page_loads(client):
    response = client.get("/checkout")

    assert response.status_code == 200
    assert b"Checkout Equipment" in response.data


def test_valid_checkout_creates_record_with_checked_out_status(client):
    response = client.post("/checkout", data=valid_checkout_form())

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/checkout")
    rows = checkout_rows()
    assert len(rows) == 1
    assert rows[0]["equipment_id"] == 1
    assert rows[0]["borrower_name"] == "Campus Borrower"
    assert rows[0]["quantity"] == 2
    assert rows[0]["return_date"] is None
    assert rows[0]["status"] == "Checked Out"


@pytest.mark.parametrize("quantity", ["0", "-1"])
def test_checkout_rejects_quantity_below_one(client, quantity):
    response = client.post(
        "/checkout", data=valid_checkout_form(quantity=quantity)
    )

    assert response.status_code == 200
    assert b"Quantity must be at least 1." in response.data
    assert checkout_rows() == []


def test_checkout_rejects_quantity_above_available_inventory(client):
    insert_checkout(quantity=7)

    response = client.post(
        "/checkout", data=valid_checkout_form(quantity="2")
    )

    assert response.status_code == 200
    assert b"Only 1 unit(s) are currently available." in response.data
    assert len(checkout_rows()) == 1


def test_checkout_rejects_blank_borrower_name(client):
    response = client.post(
        "/checkout", data=valid_checkout_form(borrower_name="   ")
    )

    assert response.status_code == 200
    assert b"Borrower name is required." in response.data
    assert checkout_rows() == []


def test_checkout_rejects_blank_borrower_email(client):
    response = client.post(
        "/checkout", data=valid_checkout_form(borrower_email="   ")
    )

    assert response.status_code == 200
    assert b"Borrower email is required." in response.data
    assert checkout_rows() == []


def test_checkout_rejects_due_date_before_checkout_date(client):
    response = client.post(
        "/checkout",
        data=valid_checkout_form(
            checkout_date=iso_date(), due_date=iso_date(-1)
        ),
    )

    assert response.status_code == 200
    assert b"Due date cannot be before the checkout date." in response.data
    assert checkout_rows() == []


def test_checkout_rejects_nonexistent_equipment(client):
    response = client.post(
        "/checkout", data=valid_checkout_form(equipment_id="9999")
    )

    assert response.status_code == 200
    assert b"selected equipment could not be found" in response.data
    assert checkout_rows() == []


def test_active_checkout_can_be_returned_and_record_is_preserved(client):
    checkout_id = insert_checkout(quantity=3)

    response = client.post(
        f"/checkout/{checkout_id}/return", follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Equipment return recorded successfully." in response.data
    rows = checkout_rows()
    assert len(rows) == 1
    assert rows[0]["return_date"] == iso_date()
    assert rows[0]["status"] == "Returned"


def test_checkout_cannot_be_returned_twice(client):
    checkout_id = insert_checkout()
    client.post(f"/checkout/{checkout_id}/return")

    response = client.post(
        f"/checkout/{checkout_id}/return", follow_redirects=True
    )

    assert b"This checkout has already been returned." in response.data
    rows = checkout_rows()
    assert len(rows) == 1
    assert rows[0]["status"] == "Returned"
    assert rows[0]["return_date"] == iso_date()


def test_past_due_active_checkout_becomes_overdue(client):
    checkout_id = insert_checkout(due_date=iso_date(-1))

    response = client.get("/checkout")

    assert response.status_code == 200
    row = next(row for row in checkout_rows() if row["id"] == checkout_id)
    assert row["status"] == "Overdue"


def test_future_due_active_checkout_remains_checked_out(client):
    checkout_id = insert_checkout(due_date=iso_date(1), status="Overdue")

    response = client.get("/checkout")

    assert response.status_code == 200
    row = next(row for row in checkout_rows() if row["id"] == checkout_id)
    assert row["status"] == "Checked Out"


def test_returned_checkout_does_not_become_overdue(client):
    checkout_id = insert_checkout(
        due_date=iso_date(-1), return_date=iso_date(), status="Returned"
    )

    response = client.get("/checkout")

    assert response.status_code == 200
    row = next(row for row in checkout_rows() if row["id"] == checkout_id)
    assert row["status"] == "Returned"


def test_checkout_history_page_loads(client):
    response = client.get("/checkout/history")

    assert response.status_code == 200
    assert b"Checkout History" in response.data


def test_returned_checkout_remains_visible_in_history(client):
    insert_checkout(
        borrower_name="Returned Borrower",
        return_date=iso_date(),
        status="Returned",
    )

    response = client.get("/checkout/history")

    assert response.status_code == 200
    assert b"Returned Borrower" in response.data
    assert b"Returned" in response.data


def test_active_checkout_appears_in_history(client):
    insert_checkout(borrower_name="Active Borrower")

    response = client.get("/checkout/history")

    assert response.status_code == 200
    assert b"Active Borrower" in response.data
    assert b"Not returned" in response.data


def test_history_shows_checkout_after_equipment_is_removed(client):
    insert_checkout(equipment_id=1, borrower_name="Historical Borrower")
    connection = campusgear.db()
    connection.execute("DELETE FROM equipment WHERE id=1")
    connection.commit()
    connection.close()

    response = client.get("/checkout/history")

    assert response.status_code == 200
    assert b"Historical Borrower" in response.data
    assert b"Removed Equipment" in response.data


def test_dashboard_totals_exclude_returned_quantities(client):
    insert_checkout(
        borrower_name="Overdue Active",
        quantity=2,
        due_date=iso_date(-1),
        status="Checked Out",
    )
    insert_checkout(
        borrower_name="Current Active",
        quantity=3,
        due_date=iso_date(1),
    )
    insert_checkout(
        borrower_name="Returned Loan",
        quantity=4,
        due_date=iso_date(-2),
        return_date=iso_date(-1),
        status="Returned",
    )

    response = client.get("/")

    assert response.status_code == 200
    assert dashboard_stat(response, "Total Units") == 33
    assert dashboard_stat(response, "Available") == 28
    assert dashboard_stat(response, "Checked Out") == 5
    assert dashboard_stat(response, "Overdue") == 2
    rows = checkout_rows()
    assert next(row for row in rows if row["borrower_name"] == "Overdue Active")["status"] == "Overdue"
    assert next(row for row in rows if row["borrower_name"] == "Returned Loan")["status"] == "Returned"


def test_equipment_without_active_loans_is_available(client):
    row = inventory_row(client.get("/equipment"), "CG-1001")

    assert row[4:7] == ["8", "0", "8"]
    assert row[9] == "Available"


def test_equipment_with_some_active_units_is_partially_checked_out(client):
    insert_checkout(equipment_id=1, quantity=3)

    row = inventory_row(client.get("/equipment"), "CG-1001")

    assert row[4:7] == ["8", "3", "5"]
    assert row[9] == "Partially Checked Out"


def test_equipment_with_all_units_borrowed_is_checked_out(client):
    insert_checkout(equipment_id=1, quantity=8)

    row = inventory_row(client.get("/equipment"), "CG-1001")

    assert row[4:7] == ["8", "8", "0"]
    assert row[9] == "Checked Out"


def test_returning_equipment_increases_available_quantity(client):
    checkout_id = insert_checkout(equipment_id=1, quantity=3)
    client.post(f"/checkout/{checkout_id}/return")

    row = inventory_row(client.get("/equipment"), "CG-1001")

    assert row[4:7] == ["8", "0", "8"]
    assert row[9] == "Available"


def test_out_of_service_condition_takes_precedence_for_availability(client):
    connection = campusgear.db()
    connection.execute(
        "UPDATE equipment SET condition='Out of Service' WHERE id=1"
    )
    connection.commit()
    connection.close()
    insert_checkout(equipment_id=1, quantity=2)

    row = inventory_row(client.get("/equipment"), "CG-1001")

    assert row[4:7] == ["8", "2", "6"]
    assert row[7] == "Out of Service"
    assert row[9] == "Out of Service"
