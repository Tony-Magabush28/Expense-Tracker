from flask import Flask, render_template, redirect, url_for, flash, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import matplotlib.pyplot as plt
import io
import base64
import csv
from fpdf import FPDF
from flask_migrate import Migrate
import math
from models import db, User, Transaction
from forms import RegisterForm, LoginForm, TransactionForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()

    today = date.today()
    monthly_expenses = sum(
        t.amount for t in transactions if t.type == 'Expense' and t.date.month == today.month and t.date.year == today.year
    )

    income = sum(t.amount for t in transactions if t.type == 'Income')
    expense = sum(t.amount for t in transactions if t.type == 'Expense')
    balance = income - expense

    if not isinstance(income, (int, float)) or math.isnan(float(income)):
        income = 0
    if not isinstance(expense, (int, float)) or math.isnan(float(expense)):
        expense = 0

    alert = None
    if current_user.budget_limit and monthly_expenses > current_user.budget_limit:
        alert = f"Warning: You have exceeded your monthly budget limit of ₵{current_user.budget_limit:.2f}!"

    chart = create_pie_chart(income, expense)

    return render_template('dashboard.html', transactions=transactions,
                           income=income, expense=expense, balance=balance,
                           chart=chart, alert=alert)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        txn = Transaction(
            user_id=current_user.id,
            amount=form.amount.data,
            category=form.category.data,
            type=form.type.data,
            date=form.date.data
        )
        db.session.add(txn)
        db.session.commit()
        flash('Transaction added!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_transaction.html', form=form)

def create_pie_chart(income, expense):
    try:
        income = float(income)
        expense = float(expense)
        if math.isnan(income):
            income = 0
        if math.isnan(expense):
            expense = 0
    except (TypeError, ValueError):
        income = 0
        expense = 0

    total = income + expense
    if total == 0:
        return None

    labels = ['Income', 'Expense']
    sizes = [income, expense]
    colors = ['#4CAF50', '#F44336']

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax.axis('equal')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    chart = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return chart

@app.route('/export/csv')
@login_required
def export_csv():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    def generate():
        data = io.StringIO()
        writer = csv.writer(data)
        writer.writerow(('Date', 'Type', 'Category', 'Amount'))
        for txn in transactions:
            writer.writerow((txn.date, txn.type, txn.category, txn.amount))
        yield data.getvalue()
        data.close()
    return Response(generate(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=transactions.csv'})

@app.route('/export/pdf')
@login_required
def export_pdf():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Transaction Report", ln=True, align='C')
    pdf.ln(10)

    for t in transactions:
        pdf.cell(200, 10, txt=f"{t.date} - {t.type} - {t.category} - ₵{t.amount}", ln=True)
    response = Response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=transactions.pdf'
    return response

@app.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    try:
        limit = float(request.form['budget_limit'])
        current_user.budget_limit = limit
        db.session.commit()
        flash("Budget limit updated.", "success")
    except ValueError:
        flash("Invalid input for budget limit. Please enter a number.", "danger")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
