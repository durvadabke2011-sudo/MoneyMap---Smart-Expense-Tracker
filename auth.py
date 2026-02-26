from flask import Blueprint, request, session, redirect, url_for, render_template, flash
import bcrypt
from datetime import datetime
from database import query

auth_bp = Blueprint('auth', __name__)


# ── DEFAULT CATEGORIES + BUDGETS SETUP ─────────────────────────
def create_default_categories(user_id):
    """
    Create default categories AND default budgets for new user.
    Called on registration. Safe to call multiple times.
    """
    try:
        income_cats = ['Salary', 'Freelance', 'Bonus', 'Investment Returns', 'Gifts', 'Other Income']
        expense_cats = [
            'Food & Dining', 'Transportation', 'Shopping', 'Utilities', 'Healthcare',
            'Entertainment', 'Education', 'Insurance', 'Home & Rent', 'Personal Care',
            'Phone & Internet', 'Gifts & Donations', 'Other Expense'
        ]

        for cat in income_cats:
            try:
                query("INSERT INTO Categories (user_id, name, type) VALUES (%s, %s, %s)",
                      (user_id, cat, 'income'))
            except Exception as e:
                print(f"Error inserting income category '{cat}': {e}")

        cat_ids = {}
        for cat in expense_cats:
            try:
                cid = query("INSERT INTO Categories (user_id, name, type) VALUES (%s, %s, %s)",
                            (user_id, cat, 'expense'), lastrowid=True)
                cat_ids[cat] = cid
            except Exception as e:
                print(f"Error inserting expense category '{cat}': {e}")

        # Default budgets for current month
        current_month = datetime.now().strftime('%Y-%m')
        default_budgets = {
            'Food & Dining':     5000,
            'Transportation':    3000,
            'Shopping':          4000,
            'Utilities':         2000,
            'Healthcare':        2000,
            'Entertainment':     2000,
            'Education':         3000,
            'Insurance':         1500,
            'Home & Rent':      10000,
            'Personal Care':     1000,
            'Phone & Internet':  1000,
            'Gifts & Donations': 1000,
            'Other Expense':     2000,
        }
        for cat_name, amount in default_budgets.items():
            cid = cat_ids.get(cat_name)
            if cid:
                try:
                    query("INSERT INTO Budgets (user_id, category_id, month, amount) VALUES (%s,%s,%s,%s)",
                          (user_id, cid, current_month, amount))
                except Exception as e:
                    print(f"Error inserting budget for '{cat_name}': {e}")

        print(f"✅ Default categories + budgets created for user {user_id}")
    except Exception as e:
        print(f"❌ Error creating defaults: {e}")


# ── REGISTER ────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        # Check duplicate
        existing = query("SELECT id FROM Users WHERE email=%s", (email,), fetch=True)
        if existing:
            flash('Email already registered. Please login.', 'error')
            return render_template('register.html')

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        uid = query(
            "INSERT INTO Users (name, email, password) VALUES (%s,%s,%s)",
            (name, email, hashed), lastrowid=True
        )
        # default preferences
        query("INSERT INTO UserPreferences (user_id) VALUES (%s)", (uid,))

        # Create default categories + budgets
        create_default_categories(uid)

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ── LOGIN ────────────────────────────────────────────────────────
@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('routes.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        rows = query("SELECT * FROM Users WHERE email=%s", (email,), fetch=True)
        if not rows:
            flash('Email not found. Please register.', 'error')
            return render_template('login.html')

        user = rows[0]
        if not bcrypt.checkpw(password.encode(), user['password'].encode()):
            flash('Incorrect password.', 'error')
            return render_template('login.html')

        # Log the login
        ip_address = request.remote_addr
        query(
            "INSERT INTO LoginHistory (user_id, ip_address) VALUES (%s, %s)",
            (user['id'], ip_address)
        )

        # Update last login time
        query(
            "UPDATE Users SET last_login=%s, last_activity=%s WHERE id=%s",
            (datetime.now(), datetime.now(), user['id'])
        )

        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return redirect(url_for('routes.dashboard'))

    return render_template('login.html')


# ── LOGOUT ───────────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))