# RiverFlood

RiverFlood is a lightweight Flask-based prototype for monitoring river water levels and presenting them through a simple early-warning dashboard. It demonstrates how sensor-like readings can be validated, processed, and displayed in a practical web application.

## Overview
This project simulates a basic flood monitoring workflow where a user can:
- submit a new water-level reading,
- validate the data on the server,
- generate derived alert information,
- and view recent readings in a dashboard.

It is designed as a demo application for learning, presentation, and prototyping rather than a production-grade deployment.

## Key Features
- **User Authentication**: Login system with account creation for secure access
- Web form for registering river readings
- Server-side validation for required fields and input values
- Automatic classification of alert status:
  - Safe
  - Warning
  - Danger
- Trend detection based on changes from the previous reading:
  - Rising
  - Falling
  - Stable
- Dashboard view for reviewing recent readings
- JSON API endpoints for reading data and simulation
- Protected routes - only authenticated users can view dashboard and register readings

## Technology Stack
- Python
- Flask
- SQLite
- HTML, CSS, and Jinja2 templates

## Project Structure
- app.py: Flask application and database logic
- templates/: HTML pages for registration and dashboard views
- static/: CSS styles for the web UI
- requirements.txt: Python dependencies
- river_flood.db: local SQLite database file generated at runtime

## Installation
1. Clone the repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open the app in your browser:
   ```text
   http://127.0.0.1:5000/
   ```

## User Authentication

### First Time Login
When you access the application for the first time, you'll be redirected to the **login page**. A demo account is pre-configured:
- **Username**: `operator`
- **Password**: `flood2026`

### Creating a New Account
If you're a new user:
1. Click **"Sign up here"** link at the bottom of the login page
2. Enter a **username** (minimum 3 characters)
3. Enter a **password** (minimum 6 characters)
4. Confirm your password
5. Click **"Create Account"**
6. You'll be redirected to the login page - login with your new credentials

### Logging Out
- Click the **"Logout"** button in the top navigation bar to end your session
- You'll be redirected to the login page

## How It Works
1. **User logs in** with their credentials on the login page
2. Upon successful authentication, user is granted access to the dashboard and registration forms
3. A user enters a river reading through the registration form
4. The Flask backend validates the input
5. The system computes derived values such as alert level, trend, and delta from the previous reading
6. The data is saved into SQLite
7. The dashboard displays the stored readings in a user-friendly format, ordered by alert urgency

## Alert Logic
- Safe: water level below 1.5 meters
- Warning: water level between 1.5 and 2.99 meters
- Danger: water level of 3.0 meters or higher

## API Endpoints
- GET /api/readings: returns all stored readings as JSON
- POST /api/simulate: inserts a simulated reading into the database

## Database
- User accounts and river readings are stored in SQLite (river_flood.db)
- The database is created automatically on first run
- Demo user (operator/flood2026) is pre-populated for testing
- New user accounts are created on demand during signup

## Security Notes
- This is a prototype designed for assessment and learning purposes
- For production use, implement proper password hashing (bcrypt/argon2)
- Session data is managed using Flask sessions with a secret key
- All protected routes require authentication

## Notes
- This is a prototype and not connected to real hardware devices.
- The local SQLite database file is created automatically when the app starts.
- The project is ideal for demonstrating backend logic, data handling, authentication, and simple dashboard UI.

