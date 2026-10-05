# CampusGear

CampusGear is a Campus Equipment Inventory System built with Flask and SQLite.

The application is designed to help a college or university keep track of equipment such as laptops, tablets, cameras, projectors, chargers, and other campus equipment.

## Main Features

- Add, edit, and delete equipment
- Search and filter equipment
- Track equipment condition and location
- Track equipment availability and status
- Check equipment out to borrowers
- Return equipment
- Track overdue equipment
- View checkout history
- Dashboard with equipment statistics

## Team Responsibilities

### Person 1 - Backend & Database Lead
- Set up and maintain the Flask project
- Create and manage the SQLite database and tables
- Build Add/Edit/Delete Equipment functionality
- Connect forms to the database
- Help with login/authentication

### Person 2 - Checkout & Dashboard Lead
- Build the checkout system
- Build the return system
- Add overdue logic
- Create checkout history
- Build dashboard totals/statistics
- Update equipment status after checkout and return

### Person 3 - Frontend, Search & Testing Lead
- Build and style application pages
- Create and improve navigation
- Style forms and equipment tables
- Add equipment search
- Add equipment filters
- Create equipment status badges
- Add error handling and user-friendly messages
- Create automated tests
- Test major application functionality

## Running CampusGear

Install the required packages:

pip install -r requirements.txt

Run the application:

python3 app.py

Then open:

http://127.0.0.1:5000

### Mac Port 5000 Note

If port 5000 is already being used, run:

python3 -m flask --app app run --debug --port 5001

Then open:

http://127.0.0.1:5001

## Technology

- Python
- Flask
- SQLite
- HTML
- CSS
- Git/GitHub
- Pytest
- Docker

## Collaboration

Each team member should work from the shared GitHub repository and make meaningful commits for their assigned portion of the project.
