from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, TextAreaField, DecimalField, SelectField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, Optional
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask import request
from sqlalchemy import Integer, String
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tracker.db"
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
# CREATE TABLE IN DB


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

class Expenses(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(nullable=False)
    transaction_type: Mapped[str] = mapped_column(nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

class FilterForm(FlaskForm):
    category = SelectField('Category', choices=[], validators=[Optional()])
    month = SelectField('Month', choices=[], validators=[Optional()])
    submit = SubmitField('Filter')

class ExpenseForm(FlaskForm):
    category = SelectField(
        'Category',
        choices=[
            ('Food & Drinks', 'Food & Drinks'),
            ('Transport', 'Transport'),
            ('Utilities', 'Utilities'),
            ('Education', 'Education'),
            ('Entertainment', 'Entertainment'),
            ('Shopping', 'Shopping'),
            ('Rent & Housing', 'Rent & Housing'),
            ('Healthcare', 'Healthcare'),
            ('Travel', 'Travel'),
            ('Financial Services', 'Financial Services')
        ],
        validators=[DataRequired()]
    )
    transaction_type = SelectField(
        'Transaction Type',
        choices=[
            ('Debit', 'Debit'),
            ('Credit', 'Credit')
        ],
        validators=[DataRequired()]
    )
    amount = DecimalField('Amount (₹)', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save')

def hash_password(password):
    hash = generate_password_hash(password=password, method='pbkdf2:sha256', salt_length=8)
    return hash
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = db.session.execute(db.select(User).where(User.email == request.form.get("email"))).scalar()
        if not user:
            new_user = User(
                email = request.form.get("email"),
                name = request.form.get("name"),
                password = hash_password(request.form.get("password"))
            )
            print(new_user.password)
            db.session.add(new_user)
            db.session.commit()

        else:
            flash("You already signed up with this email. Login instead")
        return redirect(url_for("login"))
    return render_template("register.html", logged_in=current_user.is_authenticated)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = db.session.execute(db.select(User).where(User.email == request.form.get("email"))).scalar()
        if user:
            if check_password_hash(pwhash=user.password, password=request.form.get("password")):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Incorrect password")
        else:
            flash("The email does not exist. Please try again")

    return render_template("login.html", logged_in=current_user.is_authenticated)
@app.route('/')
def home():
    categories = []
    amounts = []
    table_data = []
    if current_user.is_authenticated:
        data = db.session.query(
            Expenses.category,
            func.sum(Expenses.amount)
        ).filter(
            Expenses.transaction_type == 'Expense'
        ).group_by(
            Expenses.category
        ).all()

        categories = [item[0] for item in data]
        amounts = [item[1] for item in data]

        total_expense = sum(amounts)

        table_data = []
        for category, amount in zip(categories, amounts):
            percent = round((amount / total_expense) * 100, 1)
            table_data.append((category, amount, percent))

    return render_template('home.html', categories=categories, amounts=amounts, table_data=table_data, logged_in=current_user.is_authenticated)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    form = FilterForm()

    # Get unique categories from database
    unique_categories = db.session.query(Expenses.category).distinct().all()
    category_list = [cat[0] for cat in unique_categories]

    # List of months
    month_list = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']

    # Fill form choices dynamically
    form.category.choices = [('All', 'All Categories')] + [(cat, cat) for cat in category_list]
    form.month.choices = [('All', 'All Months')] + [(month, month) for month in month_list]

    # Get filter values
    selected_category = request.args.get('category', 'All')
    selected_month = request.args.get('month', 'All')
    page = request.args.get('page', 1, type=int)

    # Base query
    query = Expenses.query.filter_by(transaction_type='Expense')

    # Apply filters
    if selected_category != 'All':
        query = query.filter(Expenses.category == selected_category)
    if selected_month != 'All':
        query = query.filter(func.strftime('%m', Expenses.date) == str(month_list.index(selected_month)+1).zfill(2))

    # Paginate
    expenses_paginated = query.order_by(Expenses.date.desc()).paginate(page=page, per_page=10)

    return render_template('expenses.html', form=form, expenses=expenses_paginated, selected_category=selected_category, selected_month=selected_month, logged_in=current_user.is_authenticated)

@app.route('/add-expense', methods=['GET', 'POST'])
def add():
    form = ExpenseForm()

    if form.validate_on_submit():
        expense = Expenses(
            amount=form.amount.data,
            date=form.date.data,
            description=form.description.data,
            category=form.category.data,
            transaction_type = form.transaction_type.data,
        )

        db.session.add(expense)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('add_expense.html', form=form)


# @app.route('/signup')
# def signup():
#     return render_template('signup.html')
# @app.route('/charts')
# def charts():
#     expenses = Expenses.query.filter_by(transaction_type='Expense').all()
#
#     # Group by category and sum amounts
#     category_map = {}
#     for exp in expenses:
#         if exp.category in category_map:
#             category_map[exp.category] += exp.amount
#         else:
#             category_map[exp.category] = exp.amount
#
#     categories = list(category_map.keys())
#     amounts = list(category_map.values())

    return render_template('charts.html', categories=categories, amounts=amounts)
if __name__ == '__main__':
    app.run(debug=True)
