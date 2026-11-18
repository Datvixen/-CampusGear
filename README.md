# CampusGear – Campus Equipment Inventory System

**Live Website:** https://campusgear-dbzu.onrender.com

CampusGear is a Campus Equipment Inventory System built using Flask and SQLite.

The application helps colleges and universities manage equipment such as laptops, tablets, cameras, projectors, chargers, and other campus resources. It allows staff to track equipment, manage checkouts and returns, and see which items are available.

## Main Features

- Add, edit, and delete equipment
- Search and filter equipment
- Track equipment condition and location
- Track equipment availability and status
- Check equipment out to borrowers
- Return equipment
- Track overdue equipment
- View checkout history
- View equipment statistics on the dashboard

## Team Contributions

### Jamila Hayes – Website Development, Frontend, Testing & Deployment

- Created the original CampusGear website and main project structure, making it easier for teammates to add their features.
- Built and styled the website pages, navigation, forms, and equipment tables.
- Added equipment search, filters, and status labels.
- Helped combine everyone's work through GitHub and fixed errors throughout development.
- Created automated tests and tested the website's main features. During development, all 32 automated tests passed.
- Set up Docker and tested the application in a container.
- Fixed a database startup error and worked through deployment issues.
- Deployed CampusGear on Render so the completed website could be accessed online.

### Na'Shayla McIntosh – Checkout & Dashboard

- Worked on the equipment checkout and return systems.
- Added functionality for tracking overdue equipment.
- Worked on checkout history and equipment status updates.
- Built dashboard features to display equipment totals and statistics.
- Helped test the checkout and dashboard features.

### Givon Lewis – Backend & Database

- Worked on the SQLite database and SQL code.
- Helped organize and update the database tables.
- Worked on the SQL statement for the checkout table.
- Contributed to the database portion of the project.


## Running CampusGear

### 1. Install the Required Packages

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python3 app.py
```

Then open the application in your browser:

http://127.0.0.1:5000

### Mac Port 5000 Note

If port 5000 is already being used, run:

```bash
python3 -m flask --app app run --debug --port 5002
```

Then open:

http://127.0.0.1:5002

## Technology Used

- Python
- Flask
- SQLite
- HTML
- CSS
- Git/GitHub
- Pytest
- Docker
- Gunicorn
- Render

## Testing

CampusGear was tested during development to check that its main features worked properly.

The team recorded **32 passing automated tests** during development.

The application was also built and tested using Docker, and the deployed website was checked in a browser.

## Deployment

CampusGear was deployed using Docker and Render.

The website is publicly accessible at:

https://campusgear-dbzu.onrender.com

The current application includes equipment management, searching, filtering, checkout, returns, overdue tracking, and dashboard features.

The Reports / Users page is currently a placeholder. Login and authentication were not implemented in the final project.

## Collaboration

CampusGear was completed as a group project by Givon Lewis, Na'Shayla McIntosh, and Jamila Hayes.

Each team member contributed to different parts of the application. The team used GitHub to share code, combine features, and work toward completing the final website.

The original project structure allowed the team to develop their assigned features and bring them together into one working application.
