import math
import random
from datetime import date, timedelta, datetime
from functools import wraps

from flask import Blueprint, request, session, redirect, url_for, render_template, jsonify
from database import query

routes_bp = Blueprint('routes', __name__)

# ─────────────────────────────────────────────────────────────
# AUTH GUARD
# ─────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def uid():
    return session['user_id']

def _get_expense_cat(user_id, name):
    """Find expense category id by name for the user, or None."""
    row = query("SELECT id FROM Categories WHERE user_id=%s AND name=%s AND type='expense'",
                (user_id, name), fetch=True)
    return row[0]['id'] if row else None



# ─────────────────────────────────────────────────────────────
# DEFAULT CATEGORIES + BUDGETS HELPER
# ─────────────────────────────────────────────────────────────
def _create_default_categories_and_budgets(user_id):
    """Create default categories and budgets for a user. Safe to call anytime."""
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
        except Exception:
            pass

    cat_ids = {}
    for cat in expense_cats:
        try:
            cid = query("INSERT INTO Categories (user_id, name, type) VALUES (%s, %s, %s)",
                        (user_id, cat, 'expense'), lastrowid=True)
            cat_ids[cat] = cid
        except Exception:
            row = query("SELECT id FROM Categories WHERE user_id=%s AND name=%s AND type='expense'",
                        (user_id, cat), fetch=True)
            if row:
                cat_ids[cat] = row[0]['id']

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
            except Exception:
                pass

# ─────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@routes_bp.route('/api/dashboard')
@login_required
def api_dashboard():
    transactions = query(
        """SELECT t.*, c.name as category
           FROM Transactions t
           LEFT JOIN Categories c ON t.category_id=c.id
           WHERE t.user_id=%s
           ORDER BY t.date DESC LIMIT 20""",
        (uid(),), fetch=True
    )

    income = query(
        "SELECT IFNULL(SUM(amount),0) s FROM Transactions WHERE user_id=%s AND type='income'",
        (uid(),), fetch=True
    )[0]['s']

    expense = query(
        "SELECT IFNULL(SUM(amount),0) s FROM Transactions WHERE user_id=%s AND type='expense'",
        (uid(),), fetch=True
    )[0]['s']

    for t in transactions:
        t['date'] = str(t['date'])
        t['amount'] = float(t['amount'])

    # Savings goals
    goals = query("SELECT * FROM SavingsGoals WHERE user_id=%s", (uid(),), fetch=True) or []
    for g in goals:
        g['target'] = float(g['target'])
        g['saved']  = float(g['saved'])

    return jsonify({
        'transactions': transactions,
        'income': float(income),
        'expense': float(expense),
        'balance': float(income) - float(expense),
        'goals': goals
    })

# ─────────────────────────────────────────────────────────────
# SAVINGS GOALS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/api/savings-goals', methods=['POST'])
@login_required
def add_savings_goal():
    d = request.json
    query(
        "INSERT INTO SavingsGoals (user_id, name, target, saved) VALUES (%s,%s,%s,%s)",
        (uid(), d['name'], d['target'], d.get('saved', 0))
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/savings-goals/<int:gid>', methods=['DELETE'])
@login_required
def delete_savings_goal(gid):
    query("DELETE FROM SavingsGoals WHERE id=%s AND user_id=%s", (gid, uid()))
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/savings-goals/<int:gid>/add', methods=['POST'])
@login_required
def add_to_savings_goal(gid):
    """Add more money to a savings goal."""
    goal = query("SELECT * FROM SavingsGoals WHERE id=%s AND user_id=%s", (gid, uid()), fetch=True)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    d = request.json
    amount = float(d.get('amount', 0))
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    new_saved = float(goal[0]['saved']) + amount
    query("UPDATE SavingsGoals SET saved=%s WHERE id=%s AND user_id=%s", (new_saved, gid, uid()))
    return jsonify({'status': 'ok', 'new_saved': new_saved})

# ─────────────────────────────────────────────────────────────
# HEALTH SCORE
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/api/health-score')
@login_required
def health_score():
    user_id = uid()
    income = float(query(
        "SELECT IFNULL(SUM(amount),0) s FROM Transactions WHERE user_id=%s AND type='income'",
        (user_id,), fetch=True
    )[0]['s'] or 0)
    expense = float(query(
        "SELECT IFNULL(SUM(amount),0) s FROM Transactions WHERE user_id=%s AND type='expense'",
        (user_id,), fetch=True
    )[0]['s'] or 0)

    score = 50
    suggestions = []

    if income > 0:
        savings_rate = (income - expense) / income
        if savings_rate >= 0.3:
            score += 30
        elif savings_rate >= 0.1:
            score += 15
            suggestions.append('💡 Try to save at least 30% of income.')
        else:
            suggestions.append('⚠️ Savings rate is low. Cut unnecessary expenses.')

        if expense <= income:
            score += 20
        else:
            score -= 20
            suggestions.append('⚠️ Expenses exceed income! Review your spending.')
    else:
        suggestions.append('💡 Add income transactions to get a score.')

    budgets = query("SELECT COUNT(*) as cnt FROM Budgets WHERE user_id=%s", (user_id,), fetch=True)
    if budgets and budgets[0]['cnt'] > 0:
        score += 10
    else:
        suggestions.append('💡 Set budgets to better track spending.')

    score = max(0, min(100, score))

    if score >= 80:
        grade, message = 'Excellent 🌟', 'Your finances are in great shape!'
    elif score >= 60:
        grade, message = 'Good 👍', 'Doing well, keep it up!'
    elif score >= 40:
        grade, message = 'Fair ⚠️', 'Some areas need attention.'
    else:
        grade, message = 'Needs Work 🔴', 'Take action to improve your finances.'

    if not suggestions:
        suggestions.append('✅ Keep up the great financial habits!')

    return jsonify({'score': score, 'grade': grade, 'message': message, 'suggestions': suggestions})

# ─────────────────────────────────────────────────────────────
# TRANSACTIONS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/api/transactions', methods=['POST'])
@login_required
def add_transaction():
    d = request.json
    query(
        "INSERT INTO Transactions (user_id,category_id,type,amount,note,date) VALUES (%s,%s,%s,%s,%s,%s)",
        (uid(), d.get('category_id') or None, d['type'], d['amount'], d.get('note',''), d['date'])
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/transactions/<int:tid>', methods=['DELETE'])
@login_required
def delete_transaction(tid):
    query("DELETE FROM Transactions WHERE id=%s AND user_id=%s", (tid, uid()))
    return jsonify({'status': 'ok'})

# ─────────────────────────────────────────────────────────────
# INVESTMENTS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/investments')
@login_required
def investments():
    return render_template('investment.html')

@routes_bp.route('/api/investments', methods=['GET'])
@login_required
def get_investments():
    rows = query(
        "SELECT * FROM Investments WHERE user_id=%s ORDER BY invest_date DESC",
        (uid(),), fetch=True
    )
    for r in rows:
        r['amount'] = float(r['amount'])
        r['current_val'] = float(r['current_val'])
        r['invest_date'] = str(r['invest_date'])
    return jsonify(rows)

@routes_bp.route('/api/investments', methods=['POST'])
@login_required
def add_investment():
    d = request.json
    query("""
        INSERT INTO Investments (user_id, name, type, amount, current_val, invest_date, note)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (uid(), d['name'], d['type'], d['amount'],
          d.get('current_val', d['amount']), d['invest_date'], d.get('note','')))
    cat_id = _get_expense_cat(uid(), 'Other Expense')
    query(
        "INSERT INTO Transactions (user_id,category_id,type,amount,note,date) VALUES (%s,%s,%s,%s,%s,%s)",
        (uid(), cat_id, 'expense', d['amount'], f"Investment: {d['name']}", d['invest_date'])
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/investments/<int:iid>', methods=['DELETE'])
@login_required
def delete_investment(iid):
    query("DELETE FROM Investments WHERE id=%s AND user_id=%s", (iid, uid()))
    return jsonify({'status': 'ok'})

# ─────────────────────────────────────────────────────────────
# ACCOUNTS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/accounts')
@login_required
def accounts():
    return render_template('accounts.html')

@routes_bp.route('/api/accounts', methods=['GET'])
@login_required
def get_accounts():
    rows = query("SELECT * FROM Accounts WHERE user_id=%s", (uid(),), fetch=True)
    for r in rows:
        r['balance'] = float(r['balance'])
    return jsonify(rows)

@routes_bp.route('/api/accounts', methods=['POST'])
@login_required
def add_account():
    d = request.json
    query(
        "INSERT INTO Accounts (user_id,name,type,balance) VALUES (%s,%s,%s,%s)",
        (uid(), d['name'], d['type'], d.get('balance',0))
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/accounts/<int:aid>', methods=['DELETE'])
@login_required
def delete_account(aid):
    query("DELETE FROM Accounts WHERE id=%s AND user_id=%s", (aid, uid()))
    return jsonify({'status': 'ok'})

# ─────────────────────────────────────────────────────────────
# BILLS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/bills')
@login_required
def bills():
    return render_template('bills.html')

@routes_bp.route('/api/bills', methods=['GET'])
@login_required
def get_bills():
    rows = query("SELECT * FROM Bills WHERE user_id=%s", (uid(),), fetch=True)
    for r in rows:
        r['amount'] = float(r['amount'])
    return jsonify(rows)

@routes_bp.route('/api/bills', methods=['POST'])
@login_required
def add_bill():
    d = request.json
    query(
        "INSERT INTO Bills (user_id,name,amount,due_day,category) VALUES (%s,%s,%s,%s,%s)",
        (uid(), d['name'], d['amount'], d['due_day'], d.get('category','Other'))
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/bills/<int:bid>/pay', methods=['POST'])
@login_required
def pay_bill(bid):
    """Mark bill as paid — auto-creates an expense transaction."""
    bill = query("SELECT * FROM Bills WHERE id=%s AND user_id=%s", (bid, uid()), fetch=True)
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    b = bill[0]
    d = request.json
    paid_date = d.get('date', datetime.now().strftime('%Y-%m-%d'))
    # Find matching category
    cat_id = _get_expense_cat(uid(), 'Utilities')
    # Add expense transaction
    query(
        "INSERT INTO Transactions (user_id,category_id,type,amount,note,date) VALUES (%s,%s,%s,%s,%s,%s)",
        (uid(), cat_id, 'expense', float(b['amount']), f"Bill Paid: {b['name']}", paid_date)
    )
    return jsonify({'status': 'ok', 'amount': float(b['amount'])})

@routes_bp.route('/api/bills/<int:bid>', methods=['DELETE'])
@login_required
def delete_bill(bid):
    query("DELETE FROM Bills WHERE id=%s AND user_id=%s", (bid, uid()))
    return jsonify({'status': 'ok'})

# ─────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@routes_bp.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    user = query(
        "SELECT id,name,email,created_at FROM Users WHERE id=%s",
        (uid(),), fetch=True
    )[0]
    user['created_at'] = str(user['created_at'])
    prefs = query(
        "SELECT currency, theme FROM UserPreferences WHERE user_id=%s",
        (uid(),), fetch=True
    )
    preferences = prefs[0] if prefs else {'currency': 'INR', 'theme': 'light'}
    return jsonify({'user': user, 'preferences': preferences})

@routes_bp.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    d = request.json
    if 'name' in d:
        query("UPDATE Users SET name=%s WHERE id=%s", (d['name'], uid()))
        session['user_name'] = d['name']
    if 'currency' in d or 'theme' in d:
        currency = d.get('currency', 'INR')
        theme    = d.get('theme', 'light')
        query("UPDATE UserPreferences SET currency=%s, theme=%s WHERE user_id=%s",
              (currency, theme, uid()))
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    import bcrypt
    d = request.json
    user = query("SELECT password FROM Users WHERE id=%s", (uid(),), fetch=True)[0]
    if not bcrypt.checkpw(d['old_password'].encode(), user['password'].encode()):
        return jsonify({'message': 'Current password is incorrect.'}), 400
    hashed = bcrypt.hashpw(d['new_password'].encode(), bcrypt.gensalt()).decode()
    query("UPDATE Users SET password=%s WHERE id=%s", (hashed, uid()))
    return jsonify({'status': 'ok'})

# ─────────────────────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/analysis')
@login_required
def analysis():
    return render_template('analysis.html')

@routes_bp.route('/api/analysis')
@login_required
def api_analysis():
    """Return comprehensive analysis data from all pages"""
    try:
        uid_val = uid()
        months_data = {}
        today = datetime.now()

        for i in range(11, -1, -1):
            month_date = today - timedelta(days=30*i)
            month_key = month_date.strftime('%Y-%m')
            month_label = month_date.strftime('%b %Y')
            months_data[month_key] = {'label': month_label, 'income': 0, 'expense': 0}

        start_date = (today - timedelta(days=365)).strftime('%Y-%m-01')

        transactions = query(
            """SELECT DATE_FORMAT(date, '%Y-%m') as month, type, SUM(amount) as total
               FROM Transactions
               WHERE user_id=%s AND date >= %s
               GROUP BY DATE_FORMAT(date, '%Y-%m'), type""",
            (uid_val, start_date), fetch=True
        )

        if transactions:
            for t in transactions:
                month_key = t['month']
                if month_key in months_data:
                    if t['type'] == 'income':
                        months_data[month_key]['income'] = float(t['total'])
                    else:
                        months_data[month_key]['expense'] = float(t['total'])

        months, income, expense, savings = [], [], [], []
        for month_key in sorted(months_data.keys()):
            data = months_data[month_key]
            months.append(data['label'])
            inc = data['income']
            exp = data['expense']
            income.append(inc)
            expense.append(exp)
            savings.append(inc - exp)

        income_by_cat = query(
            """SELECT c.name as category, SUM(t.amount) as total
               FROM Transactions t
               LEFT JOIN Categories c ON t.category_id=c.id
               WHERE t.user_id=%s AND t.type='income' AND date >= %s
               GROUP BY c.id, c.name ORDER BY total DESC""",
            (uid_val, start_date), fetch=True
        ) or []
        income_cats = [r['category'] or 'Uncategorized' for r in income_by_cat]
        income_vals = [float(r['total']) if r['total'] else 0 for r in income_by_cat]

        expense_by_cat = query(
            """SELECT c.name as category, SUM(t.amount) as total
               FROM Transactions t
               LEFT JOIN Categories c ON t.category_id=c.id
               WHERE t.user_id=%s AND t.type='expense' AND date >= %s
               GROUP BY c.id, c.name ORDER BY total DESC""",
            (uid_val, start_date), fetch=True
        ) or []
        expense_cats = [r['category'] or 'Uncategorized' for r in expense_by_cat]
        expense_vals = [float(r['total']) if r['total'] else 0 for r in expense_by_cat]

        accounts = query(
            "SELECT type, SUM(balance) as total FROM Accounts WHERE user_id=%s GROUP BY type",
            (uid_val,), fetch=True
        ) or []
        account_types  = [a['type'].upper() if a['type'] else 'Unknown' for a in accounts]
        account_values = [float(a['total']) if a['total'] else 0 for a in accounts]

        investments = query(
            "SELECT type, COUNT(*) as count, SUM(current_val) as total FROM Investments WHERE user_id=%s GROUP BY type ORDER BY total DESC",
            (uid_val,), fetch=True
        ) or []
        inv_types  = [inv['type'] or 'Other' for inv in investments]
        inv_counts = [int(inv['count']) for inv in investments]
        inv_values = [float(inv['total']) if inv['total'] else 0 for inv in investments]

        bills = query(
            "SELECT category, COUNT(*) as count, SUM(amount) as total FROM Bills WHERE user_id=%s GROUP BY category ORDER BY total DESC LIMIT 10",
            (uid_val,), fetch=True
        ) or []
        bill_cats   = [b['category'] or 'Other' for b in bills]
        bill_counts = [int(b['count']) for b in bills]
        bill_vals   = [float(b['total']) if b['total'] else 0 for b in bills]

        subscriptions = query(
            "SELECT name, amount FROM Subscriptions WHERE user_id=%s ORDER BY amount DESC LIMIT 10",
            (uid_val,), fetch=True
        ) or []
        sub_names  = [s['name'][:15] for s in subscriptions]
        sub_values = [float(s['amount']) for s in subscriptions]

        # ─── TRIPS (fixed: uses TripExpenses JOIN) ───────────────
        trips = query(
            """SELECT t.destination, COALESCE(SUM(te.amount), 0) as spent
               FROM Trips t
               LEFT JOIN TripExpenses te ON te.trip_id = t.id
               WHERE t.user_id=%s
               GROUP BY t.id, t.destination
               ORDER BY spent DESC LIMIT 10""",
            (uid_val,), fetch=True
        ) or []
        trip_names  = [t['destination'][:15] for t in trips]
        trip_values = [float(t['spent']) if t['spent'] else 0 for t in trips]

        loans = query(
            "SELECT loan_name, principal, emi, total_int FROM Loans WHERE user_id=%s ORDER BY principal DESC LIMIT 10",
            (uid_val,), fetch=True
        ) or []
        loan_names      = [l['loan_name'][:15] for l in loans]
        loan_principals = [float(l['principal']) for l in loans]
        loan_emis       = [float(l['emi']) if l['emi'] else 0 for l in loans]
        loan_interests  = [float(l['total_int']) if l['total_int'] else 0 for l in loans]

        budgets = query(
            """SELECT b.amount, c.name
               FROM Budgets b
               LEFT JOIN Categories c ON b.category_id=c.id
               WHERE b.user_id=%s
               ORDER BY b.amount DESC LIMIT 10""",
            (uid_val,), fetch=True
        ) or []
        budget_cats = [bg['name'][:15] for bg in budgets if bg['name']]
        budget_vals = [float(bg['amount']) if bg['amount'] else 0 for bg in budgets if bg['name']]

        return jsonify({
            'months': months, 'income': income, 'expense': expense, 'savings': savings,
            'income_categories': income_cats, 'income_values': income_vals,
            'expense_categories': expense_cats, 'expense_values': expense_vals,
            'account_types': account_types, 'account_values': account_values,
            'inv_types': inv_types, 'inv_counts': inv_counts, 'inv_values': inv_values,
            'bill_categories': bill_cats, 'bill_counts': bill_counts, 'bill_values': bill_vals,
            'subscription_names': sub_names, 'subscription_values': sub_values,
            'trip_names': trip_names, 'trip_values': trip_values,
            'loan_names': loan_names, 'loan_principals': loan_principals,
            'loan_emis': loan_emis, 'loan_interests': loan_interests,
            'budget_categories': budget_cats, 'budget_values': budget_vals
        })
    except Exception as e:
        print(f"Analysis API error: {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500

# ─────────────────────────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/categories')
@login_required
def categories():
    return render_template('categories.html')

@routes_bp.route('/api/categories')
@login_required
def get_categories():
    user_id = uid()
    existing = query("SELECT COUNT(*) as cnt FROM Categories WHERE user_id=%s", (user_id,), fetch=True)
    if existing and existing[0]['cnt'] == 0:
        _create_default_categories_and_budgets(user_id)
    rows = query("SELECT * FROM Categories WHERE user_id=%s ORDER BY type, name", (user_id,), fetch=True)
    return jsonify(rows)

@routes_bp.route('/api/setup-defaults', methods=['POST'])
@login_required
def setup_defaults():
    """Repair endpoint: re-create missing categories/budgets for existing users."""
    _create_default_categories_and_budgets(uid())
    return jsonify({'status': 'ok', 'message': 'Defaults created'})

@routes_bp.route('/api/categories', methods=['POST'])
@login_required
def add_category():
    d = request.json
    query(
        "INSERT INTO Categories (user_id,name,type) VALUES (%s,%s,%s)",
        (uid(), d['name'], d['type'])
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/categories/<int:cid>', methods=['DELETE'])
@login_required
def delete_category(cid):
    query("DELETE FROM Categories WHERE id=%s AND user_id=%s", (cid, uid()))
    return jsonify({'status': 'ok'})

# ─────────────────────────────────────────────────────────────
# BUDGETS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/budgets')
@login_required
def budgets():
    return render_template('budgets.html')

@routes_bp.route('/api/budgets')
@login_required
def get_budgets():
    rows = query("""SELECT b.id, b.amount, b.month, b.category_id, c.name as category_name
                    FROM Budgets b
                    LEFT JOIN Categories c ON b.category_id=c.id
                    WHERE b.user_id=%s""", (uid(),), fetch=True)
    for r in rows:
        r['amount'] = float(r['amount'])
    return jsonify(rows)

@routes_bp.route('/api/budgets', methods=['POST'])
@login_required
def add_budget():
    d = request.json
    query(
        "INSERT INTO Budgets (user_id,category_id,month,amount) VALUES (%s,%s,%s,%s)",
        (uid(), d.get('category_id'), d['month'], d['amount'])
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/budgets/<int:bid>', methods=['DELETE'])
@login_required
def delete_budget(bid):
    query("DELETE FROM Budgets WHERE id=%s AND user_id=%s", (bid, uid()))
    return jsonify({'status': 'ok'})

# ─────────────────────────────────────────────────────────────
# TRIPS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/trips')
@login_required
def trips():
    return render_template('trips.html')

@routes_bp.route('/api/trips')
@login_required
def get_trips():
    rows = query("SELECT * FROM Trips WHERE user_id=%s", (uid(),), fetch=True)
    for r in rows:
        r['budget'] = float(r['budget'])
        r['start_date'] = str(r['start_date'])
        r['end_date'] = str(r['end_date'])
        spent_row = query(
            "SELECT COALESCE(SUM(amount), 0) as total FROM TripExpenses WHERE trip_id=%s",
            (r['id'],), fetch=True
        )
        r['spent'] = float(spent_row[0]['total']) if spent_row else 0.0
    return jsonify(rows)

@routes_bp.route('/api/trips', methods=['POST'])
@login_required
def add_trip():
    d = request.json
    query(
        "INSERT INTO Trips (user_id,destination,start_date,end_date,budget) VALUES (%s,%s,%s,%s,%s)",
        (uid(), d['destination'], d['start_date'], d['end_date'], d.get('budget', 0))
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/trips/<int:tid>/expenses', methods=['POST'])
@login_required
def add_trip_expense(tid):
    trip = query("SELECT id FROM Trips WHERE id=%s AND user_id=%s", (tid, uid()), fetch=True)
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    d = request.json
    query(
        "INSERT INTO TripExpenses (trip_id, note, amount, date) VALUES (%s,%s,%s,%s)",
        (tid, d.get('note', ''), d['amount'], d['date'])
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/trips/<int:tid>', methods=['DELETE'])
@login_required
def delete_trip(tid):
    query("DELETE FROM Trips WHERE id=%s AND user_id=%s", (tid, uid()))
    return jsonify({'status': 'ok'})

# ─────────────────────────────────────────────────────────────
# SUBSCRIPTIONS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/subscriptions')
@login_required
def subscriptions():
    return render_template('subscriptions.html')

@routes_bp.route('/api/subscriptions')
@login_required
def get_subscriptions():
    rows = query("SELECT * FROM Subscriptions WHERE user_id=%s", (uid(),), fetch=True)
    today = datetime.now().date()
    for r in rows:
        r['amount'] = float(r['amount'])
        # Calculate next renewal date
        renewal_day = int(r['renewal_day'])
        next_renewal = today.replace(day=renewal_day)
        if next_renewal <= today:
            # Move to next month
            if today.month == 12:
                next_renewal = next_renewal.replace(year=today.year+1, month=1)
            else:
                next_renewal = next_renewal.replace(month=today.month+1)
        r['next_renewal'] = str(next_renewal)
        r['days_left'] = (next_renewal - today).days
    return jsonify(rows)

@routes_bp.route('/api/subscriptions', methods=['POST'])
@login_required
def add_subscription():
    d = request.json
    query(
        "INSERT INTO Subscriptions (user_id,name,amount,renewal_day) VALUES (%s,%s,%s,%s)",
        (uid(), d['name'], d['amount'], d['renewal_day'])
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/subscriptions/<int:sid>', methods=['DELETE'])
@login_required
def delete_subscription(sid):
    query("DELETE FROM Subscriptions WHERE id=%s AND user_id=%s", (sid, uid()))
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/subscriptions/<int:sid>/pay', methods=['POST'])
@login_required
def pay_subscription(sid):
    """Mark subscription as paid — auto-creates an expense transaction."""
    sub = query("SELECT * FROM Subscriptions WHERE id=%s AND user_id=%s", (sid, uid()), fetch=True)
    if not sub:
        return jsonify({'error': 'Subscription not found'}), 404
    s = sub[0]
    d = request.json
    paid_date = d.get('date', datetime.now().strftime('%Y-%m-%d'))
    cat_id = _get_expense_cat(uid(), 'Phone & Internet')
    query(
        "INSERT INTO Transactions (user_id,category_id,type,amount,note,date) VALUES (%s,%s,%s,%s,%s,%s)",
        (uid(), cat_id, 'expense', float(s['amount']), f"Subscription: {s['name']}", paid_date)
    )
    return jsonify({'status': 'ok', 'amount': float(s['amount'])})

# ─────────────────────────────────────────────────────────────
# EMI TRACKER
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/emi-tracker')
@login_required
def emi_tracker():
    return render_template('emi_tracker.html')

@routes_bp.route('/api/loans')
@login_required
def get_loans():
    rows = query("SELECT * FROM Loans WHERE user_id=%s", (uid(),), fetch=True)

    for r in rows:
        r['principal'] = float(r['principal'])
        r['rate'] = float(r['rate'])
        r['emi'] = float(r['emi']) if r['emi'] else 0
        r['total_int'] = float(r['total_int']) if r['total_int'] else 0
        r['tenure'] = int(r['tenure'])

        payments = query(
            "SELECT SUM(amount) as total FROM EmiPayments WHERE loan_id=%s",
            (r['id'],), fetch=True
        )
        amount_paid = float(payments[0]['total']) if payments[0]['total'] else 0
        r['amount_paid'] = amount_paid
        r['amount_left'] = (r['principal'] + r['total_int']) - amount_paid

        months_paid = int(amount_paid / r['emi']) if r['emi'] > 0 else 0
        r['months_paid'] = months_paid
        r['months_left'] = max(0, r['tenure'] - months_paid)
        r['progress_pct'] = 0 if r['tenure'] == 0 else int((months_paid / r['tenure']) * 100)

        created = r['created_at']
        next_due_date = created + timedelta(days=30 * (months_paid + 1))
        r['next_due'] = next_due_date.strftime('%Y-%m-%d')

        today = datetime.now()
        r['days_to_due'] = (next_due_date.date() - today.date()).days

    return jsonify(rows)

@routes_bp.route('/api/loans', methods=['POST'])
@login_required
def add_loan():
    d = request.json
    principal = float(d['principal'])
    rate = float(d['rate']) / 12 / 100
    tenure = int(d['tenure']) * 12

    emi = principal * rate * ((1 + rate) ** tenure) / (((1 + rate) ** tenure) - 1)
    total_int = (emi * tenure) - principal

    query(
        "INSERT INTO Loans (user_id,loan_name,principal,rate,tenure,emi,total_int) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (uid(), d.get('loan_name', 'My Loan'), principal, d['rate'], tenure, emi, total_int)
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/emi-calc', methods=['POST'])
@login_required
def emi_calc():
    return add_loan()

@routes_bp.route('/api/loans/<int:lid>', methods=['DELETE'])
@login_required
def delete_loan(lid):
    query("DELETE FROM Loans WHERE id=%s AND user_id=%s", (lid, uid()))
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/loans/<int:lid>/pay', methods=['POST'])
@login_required
def pay_emi(lid):
    d = request.json
    amt  = float(d['amount'])
    date = d['date']
    note = d.get('note', '')
    # Save to EMI payment history
    query(
        "INSERT INTO EmiPayments (loan_id, paid_date, amount, note) VALUES (%s, %s, %s, %s)",
        (lid, date, amt, note)
    )
    # Get loan name for transaction note
    loan = query("SELECT loan_name FROM Loans WHERE id=%s AND user_id=%s", (lid, uid()), fetch=True)
    loan_name = loan[0]['loan_name'] if loan else 'EMI'
    # Auto-add as expense transaction
    cat_id = _get_expense_cat(uid(), 'Insurance')
    query(
        "INSERT INTO Transactions (user_id,category_id,type,amount,note,date) VALUES (%s,%s,%s,%s,%s,%s)",
        (uid(), cat_id, 'expense', amt, f"EMI Paid: {loan_name}", date)
    )
    return jsonify({'status': 'ok'})

@routes_bp.route('/api/loans/<int:lid>/payments')
@login_required
def get_loan_payments(lid):
    rows = query(
        "SELECT * FROM EmiPayments WHERE loan_id=%s ORDER BY paid_date DESC",
        (lid,), fetch=True
    )
    for r in rows:
        r['amount'] = float(r['amount'])
    return jsonify(rows)

# ─────────────────────────────────────────────────────────────
# ADMIN ANALYTICS
# ─────────────────────────────────────────────────────────────
@routes_bp.route('/admin/stats')
def admin_stats_page():
    return render_template('admin_stats.html')

@routes_bp.route('/api/admin/stats')
def api_admin_stats():
    total_users = query("SELECT COUNT(*) as count FROM Users", fetch=True)[0]['count']
    users_by_date = query(
        "SELECT DATE(created_at) as date, COUNT(*) as count FROM Users GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 30",
        fetch=True
    )
    all_users = query(
        """SELECT u.id, u.name, u.email, u.created_at, u.last_login,
            (SELECT COUNT(*) FROM Transactions WHERE user_id=u.id) as transaction_count,
            (SELECT COUNT(*) FROM LoginHistory WHERE user_id=u.id) as login_count
           FROM Users u ORDER BY u.last_login DESC""",
        fetch=True
    )
    for user in all_users:
        user['created_at'] = str(user['created_at']) if user['created_at'] else 'N/A'
        user['last_login'] = str(user['last_login']) if user['last_login'] else 'Never'
    return jsonify({'total_users': total_users, 'users_by_date': users_by_date, 'all_users': all_users})

@routes_bp.route('/api/admin/login-history/<int:user_id>')
def api_admin_login_history(user_id):
    logins = query(
        """SELECT id, login_time, ip_address FROM LoginHistory
           WHERE user_id=%s ORDER BY login_time DESC LIMIT 50""",
        (user_id,), fetch=True
    )
    for login in logins:
        login['login_time'] = str(login['login_time'])
    return jsonify(logins)