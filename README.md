# Habit Tracker

A web-based habit tracking application built using **Flask** and **SQLAlchemy**, designed to track daily habits and provide meaningful insights through weekly and monthly analytics.

The project emphasizes **clean backend logic, efficient data handling, and practical analytics**, while keeping the user interface simple and functional.

---

## Features

* Add and manage daily habits
* Track habit completion on a day-by-day basis
* Weekly habit overview with daily breakdown
* Search habits by name (case-insensitive)
* Weekly performance analytics
* Monthly habit analytics
* Habit consistency calculation
* Dynamic streak tracking without database changes

---

## Tech Stack

* **Backend:** Python, Flask
* **Database:** SQLite
* **ORM:** SQLAlchemy
* **Frontend:** HTML, Bootstrap, jQuery
* **Charts:** Chart.js

---

## Project Structure

```
habit-tracker/
│
├── app.py                  # Flask application and API routes
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── templates/
│   ├── index.html          # Main habit tracker page
│   └── analytics.html      # Analytics dashboard
├── static/
│   ├── app.js              # Frontend logic
│   └── styles.css          # Custom styles
```

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/Abilash1803/Habit-tracker.git
cd habit-tracker
```

### 2. Create and activate a virtual environment

**Windows**

```cmd
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

---

## Application Access

* **Main Application:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
* **Analytics Dashboard:** [http://127.0.0.1:5000/analytics](http://127.0.0.1:5000/analytics)

---

## Notes

* Analytics such as streaks and consistency are computed dynamically.
* No database schema changes are required for analytics features.
* The application uses SQLite for simplicity and local persistence.


