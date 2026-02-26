# 💰 MoneyMap – Personal Finance Management System

A complete, full-stack personal finance web application built with Python Flask, MySQL, and Vanilla JavaScript.

---

## 🚀 Features

- 🔐 Email + Password Authentication (session-based, no Google login)
- 🏠 Dashboard with income, expense, savings overview
- 📊 Analysis charts (Chart.js) – monthly income vs expense
- 🗂️ Categories CRUD (income & expense)
- 💰 Monthly budget management with overspend alerts
- ✈️ Trip expense tracking
- 🧾 Accounts (Cash / Card / UPI)
- 🔔 Bill reminders (Electricity, Rent, EMI, Credit Card)
- 🧮 EMI / Loan Calculator
- 🏦 Mock Bank API transactions
- 📺 Subscription tracker (Netflix, Spotify, etc.)
- ❤️ Financial Health Score (0–100)
- 🤖 Smart financial suggestions

---

## 🛠️ Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Frontend   | HTML, CSS, Vanilla JS   |
| Backend    | Python Flask            |
| Database   | MySQL                   |
| Charts     | Chart.js                |
| Auth       | Session-based (bcrypt)  |

---

## 📁 Folder Structure

```
MoneyMap/
├── README.md           ← This file
├── app.py              ← Flask app entry point
├── config.py           ← DB config & secret key
├── database.py         ← DB connection helper
├── models.py           ← All SQL table creation
├── auth.py             ← Login, register, logout routes
├── routes.py           ← All feature routes
├── requirements.txt    ← Python dependencies
│
├── static/
│   ├── css/style.css   ← Global styles
│   └── js/main.js      ← Frontend JS (fetch API calls)
│
└── templates/
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── analysis.html
    ├── categories.html
    ├── budgets.html
    ├── trips.html
    ├── accounts.html
    ├── subscriptions.html
    ├── bills.html
    └── settings.html
```

---

## 🗄️ Database Setup (MySQL)

1. Open MySQL Workbench or terminal
2. Create the database:

```sql
CREATE DATABASE moneymap;
```

3. Update `config.py` with your MySQL credentials.

---

## ⚙️ Environment Variables (config.py)

Edit `config.py`:

```python
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'your_mysql_password'
DB_NAME = 'moneymap'
SECRET_KEY = 'your_secret_key_here'
```

---

## ▶️ Steps to Run in VS Code

1. **Clone / download** the project folder into VS Code
2. Open terminal in VS Code (`Ctrl + \``)
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create MySQL database:

```sql
CREATE DATABASE moneymap;
```

5. Update your credentials in `config.py`

6. Run the app:

```bash
python app.py
```

7. Open browser → [http://localhost:5000](http://localhost:5000)

---

## 🔑 Sample Test Credentials

After registering, use:

- **Email:** test@moneymap.com
- **Password:** Test@1234

---

## 📌 Notes

- All data persists in MySQL on page refresh
- No Google/OAuth login — only email + password
- Session expires on logout
