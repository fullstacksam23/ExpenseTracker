from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, DecimalField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Optional
from datetime import date
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tracker.db"
db.init_app(app)


class Expenses(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(nullable=False)
    transaction_type: Mapped[str] = mapped_column(nullable=False)

with app.app_context():
    db.create_all()

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
    transaction_type = SelectField(  # 🆕 Added field
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

@app.route('/')
def home():
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

    return render_template('home.html', categories=categories, amounts=amounts, table_data=table_data)


@app.route('/expenses')
def expenses():
    return render_template('expenses.html')
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
# @app.route('/login')
# def login():
#     return render_template('login.html')
#
# @app.route('/signup')
# def signup():
#     return render_template('signup.html')
@app.route('/charts')
def charts():
    expenses = Expenses.query.filter_by(transaction_type='Expense').all()

    # Group by category and sum amounts
    category_map = {}
    for exp in expenses:
        if exp.category in category_map:
            category_map[exp.category] += exp.amount
        else:
            category_map[exp.category] = exp.amount

    categories = list(category_map.keys())
    amounts = list(category_map.values())

    return render_template('charts.html', categories=categories, amounts=amounts)
if __name__ == '__main__':
    app.run(debug=True)
