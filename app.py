from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from database import Database
from datetime import datetime
import calendar
import bcrypt
import json
import os

app = Flask(__name__)
app.secret_key = 'wealthwise-neural-hub-secret-key-2026'  # Change in production

db = Database()

DIARY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diary_rich_data.json')


# ──────────────────────────────────────────────
#  AUTH MIDDLEWARE
# ──────────────────────────────────────────────
def login_required(f):
    """Decorator to protect routes that need authentication"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ──────────────────────────────────────────────
#  AUTH ROUTES
# ──────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html', mode='login')

        db.execute("SELECT id, username, monthly_limit, daily_limit, password FROM users WHERE username=%s", (username,))
        res = db.cursor.fetchone()

        if res:
            stored_pw = res[4]
            authenticated = False
            try:
                # Try bcrypt verification first
                if bcrypt.checkpw(password.encode('utf-8'), stored_pw.encode('utf-8')):
                    authenticated = True
            except Exception:
                # Fallback to plain-text comparison (legacy accounts)
                if password == stored_pw:
                    authenticated = True

            if authenticated:
                session['user_id'] = res[0]
                session['username'] = res[1]
                session['monthly_limit'] = float(res[2])
                session['daily_limit'] = float(res[3])
                return redirect(url_for('dashboard'))

        flash('Access Denied — Invalid credentials', 'error')

    return render_template('login.html', mode='login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html', mode='register')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            db.execute("INSERT INTO users (username, password, monthly_limit, daily_limit) VALUES (%s,%s,5000,500)", (username, hashed))
            db.commit()
            flash('Account Encrypted! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {e}', 'error')

    return render_template('login.html', mode='register')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ──────────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────────
@app.route('/')
@login_required
def dashboard():
    user_id = session['user_id']
    m_limit = session.get('monthly_limit', 5000)
    d_limit = session.get('daily_limit', 500)

    now = datetime.now()
    this_month = now.strftime('%Y-%m')

    db.execute("SELECT amount, category, date FROM expense WHERE user_id=%s AND date LIKE %s ORDER BY date DESC",
               (user_id, f"{this_month}%"))
    res = db.cursor.fetchall()

    spent = sum(float(x[0]) for x in res) if res else 0.0
    remaining = max(0, m_limit - spent)
    percent_used = int((spent / m_limit) * 100) if m_limit > 0 else 100

    days_in_mo = calendar.monthrange(now.year, now.month)[1]
    days_left = max(1, days_in_mo - now.day)
    safe_amt = remaining / days_left

    is_failing = remaining <= 0
    transactions = res[:5] if res else []

    return render_template('dashboard.html',
                           active_page='dashboard',
                           m_limit=m_limit,
                           d_limit=d_limit,
                           spent=spent,
                           remaining=remaining,
                           percent_used=percent_used,
                           safe_amt=safe_amt,
                           is_failing=is_failing,
                           transactions=transactions)


# ──────────────────────────────────────────────
#  CHART DATA API
# ──────────────────────────────────────────────
@app.route('/api/chart-data')
@login_required
def chart_data():
    user_id = session['user_id']
    view = request.args.get('view', 'monthly')  # 'weekly' or 'monthly'
    now = datetime.now()

    # Use LIKE match for categories (handles emoji encoding quirks)
    categories = [
        {'name': 'FOOD',      'match': '%FOOD',      'color': '#ef4444'},
        {'name': 'TRANSPORT',  'match': '%TRANSPORT',  'color': '#3b82f6'},
        {'name': 'BILLS',     'match': '%BILLS',     'color': '#f59e0b'},
        {'name': 'FUN',       'match': '%FUN',       'color': '#8b5cf6'},
        {'name': 'STUDIES',   'match': '%STUDIES',   'color': '#10b981'},
        {'name': 'OTHER',     'match': '%OTHER',     'color': '#6b7280'},
    ]

    if view == 'weekly':
        labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        week_ranges = [(1, 7), (8, 14), (15, 21), (22, 31)]
        datasets = []

        for cat in categories:
            data_points = []
            for s, e in week_ranges:
                val = db.query_value(
                    "SELECT COALESCE(SUM(amount), 0) FROM expense "
                    "WHERE user_id=%s AND MONTH(date)=%s AND YEAR(date)=%s "
                    "AND DAY(date) BETWEEN %s AND %s AND category LIKE %s",
                    (user_id, now.month, now.year, s, e, cat['match'])
                )
                data_points.append(val)

            datasets.append({
                'label': cat['name'],
                'data': data_points,
                'backgroundColor': cat['color'],
                'borderColor': cat['color'],
                'borderWidth': 1,
                'borderRadius': 4
            })
    else:
        labels = []
        month_keys = []
        for i in range(5, -1, -1):
            m = now.month - i
            y = now.year
            if m <= 0:
                m += 12
                y -= 1
            labels.append(datetime(y, m, 1).strftime('%b %Y'))
            month_keys.append((y, m))

        datasets = []
        for cat in categories:
            data_points = []
            for y, m in month_keys:
                val = db.query_value(
                    "SELECT COALESCE(SUM(amount), 0) FROM expense "
                    "WHERE user_id=%s AND MONTH(date)=%s AND YEAR(date)=%s AND category LIKE %s",
                    (user_id, m, y, cat['match'])
                )
                data_points.append(val)

            datasets.append({
                'label': cat['name'],
                'data': data_points,
                'backgroundColor': cat['color'],
                'borderColor': cat['color'],
                'borderWidth': 1,
                'borderRadius': 4
            })

    # Pie/doughnut for current month
    pie_data = []
    pie_labels = []
    pie_colors = []
    for cat in categories:
        val = db.query_value(
            "SELECT COALESCE(SUM(amount), 0) FROM expense "
            "WHERE user_id=%s AND MONTH(date)=%s AND YEAR(date)=%s AND category LIKE %s",
            (user_id, now.month, now.year, cat['match'])
        )
        if val > 0:
            pie_data.append(val)
            pie_labels.append(cat['name'])
            pie_colors.append(cat['color'])

    return jsonify({
        'bar': {'labels': labels, 'datasets': datasets},
        'pie': {'labels': pie_labels, 'data': pie_data, 'colors': pie_colors}
    })


# ──────────────────────────────────────────────
#  ANALYSIS (SPENDING DATA)
# ──────────────────────────────────────────────
@app.route('/analysis')
@login_required
def analysis():
    user_id = session['user_id']
    month = datetime.now().month

    weeks_config = [
        ("Week 1 (1-7)", 1, 7),
        ("Week 2 (8-14)", 8, 14),
        ("Week 3 (15-21)", 15, 21),
        ("Week 4 (22-31)", 22, 31),
    ]

    weeks = []
    for name, s, e in weeks_config:
        db.execute("SELECT id, amount, category, description, date FROM expense "
                   "WHERE user_id=%s AND MONTH(date)=%s AND DAY(date) BETWEEN %s AND %s ORDER BY date DESC",
                   (user_id, month, s, e))
        rows = db.cursor.fetchall()
        weeks.append((name, rows))

    return render_template('analysis.html', active_page='analysis', weeks=weeks)


# ──────────────────────────────────────────────
#  DELETE EXPENSE
# ──────────────────────────────────────────────
@app.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    db.execute("DELETE FROM expense WHERE id=%s AND user_id=%s", (expense_id, session['user_id']))
    db.commit()
    flash('Transaction removed from records.', 'success')
    return redirect(url_for('analysis'))


# ──────────────────────────────────────────────
#  ADD EXPENSE
# ──────────────────────────────────────────────
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            category = request.form.get('category', '')
            description = request.form.get('description', '')

            db.execute("INSERT INTO expense (user_id, amount, category, description, date) VALUES (%s,%s,%s,%s,%s)",
                       (session['user_id'], amount, category, description, datetime.now().strftime('%Y-%m-%d')))
            db.commit()
            flash('Expense added to your records.', 'success')
            return redirect(url_for('dashboard'))
        except Exception:
            flash('Please enter a valid amount.', 'error')

    return render_template('add.html', active_page='add')


# ──────────────────────────────────────────────
#  RECOVERY (BUDGET CLINIC)
# ──────────────────────────────────────────────
@app.route('/recovery')
@login_required
def recovery():
    user_id = session['user_id']
    limit = session.get('monthly_limit', 5000)
    now = datetime.now()

    db.execute("SELECT SUM(amount) FROM expense WHERE user_id=%s AND date LIKE %s",
               (user_id, f"{now.strftime('%Y-%m')}%"))
    res = db.cursor.fetchone()[0]
    spent = float(res) if res else 0.0

    is_over = spent > limit
    progress = min(int((spent / limit) * 100), 100) if limit > 0 else 0
    debt = spent - limit if is_over else 0
    days_left = max(1, calendar.monthrange(now.year, now.month)[1] - now.day)
    daily_cut = debt / days_left if is_over else 0

    return render_template('recovery.html',
                           active_page='recovery',
                           spent=spent,
                           limit=limit,
                           is_over=is_over,
                           progress=progress,
                           debt=debt,
                           daily_cut=daily_cut)


# ──────────────────────────────────────────────
#  SETTINGS (CHANGE TARGETS)
# ──────────────────────────────────────────────
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        monthly = request.form.get('monthly', session.get('monthly_limit', 5000))
        daily = request.form.get('daily', session.get('daily_limit', 500))

        db.execute("UPDATE users SET monthly_limit=%s, daily_limit=%s WHERE id=%s",
                   (monthly, daily, session['user_id']))
        db.commit()

        session['monthly_limit'] = float(monthly)
        session['daily_limit'] = float(daily)

        flash('Targets updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('settings.html',
                           active_page='settings',
                           current_monthly=session.get('monthly_limit', 5000),
                           current_daily=session.get('daily_limit', 500))


# ──────────────────────────────────────────────
#  PLANNER + DIARY
# ──────────────────────────────────────────────
@app.route('/planner')
@login_required
def planner():
    # Load diary pages
    pages = {str(i): "" for i in range(1, 51)}
    if os.path.exists(DIARY_PATH):
        try:
            with open(DIARY_PATH, 'r') as f:
                pages.update(json.load(f))
        except Exception:
            pass

    return render_template('planner.html', active_page='planner', diary_pages=pages)


@app.route('/planner/save', methods=['POST'])
@login_required
def save_planner():
    data = request.get_json()
    if data and 'pages' in data:
        try:
            with open(DIARY_PATH, 'w') as f:
                json.dump(data['pages'], f)
            return jsonify({'status': 'ok'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': 'No data'}), 400


# ──────────────────────────────────────────────
#  EXPORT PDF
# ──────────────────────────────────────────────
@app.route('/export-pdf')
@login_required
def export_pdf():
    try:
        from fpdf import FPDF

        db.execute("SELECT date, category, amount, description FROM expense WHERE user_id=%s ORDER BY date DESC",
                   (session['user_id'],))
        rows = db.cursor.fetchall()

        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 15, "WEALTHWISE FINANCIAL AUDIT LOG", 0, 1, 'C', 1)

        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12)

        # Header
        pdf.cell(30, 10, "DATE", 1)
        pdf.cell(40, 10, "CATEGORY", 1)
        pdf.cell(30, 10, "AMOUNT", 1)
        pdf.cell(90, 10, "DESCRIPTION", 1)
        pdf.ln()

        pdf.set_font("Arial", '', 10)
        for r in rows:
            pdf.cell(30, 10, str(r[0]), 1)
            pdf.cell(40, 10, str(r[1]), 1)
            pdf.cell(30, 10, f"Rs.{r[2]}", 1)
            pdf.cell(90, 10, str(r[3])[:40], 1)
            pdf.ln()

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'My_Wealth_Report.pdf')
        pdf.output(output_path)

        return send_file(output_path, as_attachment=True, download_name='My_Wealth_Report.pdf')
    except Exception as e:
        flash(f'PDF export failed: {e}', 'error')
        return redirect(url_for('analysis'))


# ──────────────────────────────────────────────
#  RUN
# ──────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)
