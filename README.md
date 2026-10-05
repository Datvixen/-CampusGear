# CampusGear

Campus Equipment Inventory System built with Flask and SQLite.

## Your completed starter portion
- Styled dashboard
- SQLite database
- Add/edit/delete equipment
- Search inventory
- Category, condition, and location dropdown filters
- Starter data
- Dockerfile and automated-test starter

## Team Member 2
Build checkout, borrower/due dates, returns, and checkout history.

## Team Member 3
Build user management, overdue equipment, reports/activity, and additional tests.

## Run on Windows
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Suggested Git branches
- feature/equipment-management
- feature/checkout-system
- feature/users-reports



Open the application in your browser:

http://127.0.0.1:5000

If port 5000 is already in use, run the app on port 5001:

python3 -m flask --app app run --debug --port 5001

Then open:

http://127.0.0.1:5001
