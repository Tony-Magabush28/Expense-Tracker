from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, message="Username must be at least 3 characters.")
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address.")
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required."),
            Length(min=6, message="Password must be at least 6 characters.")
        ]
    )
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address.")
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message="Password is required.")]
    )
    submit = SubmitField('Login')

class TransactionForm(FlaskForm):
    amount = FloatField(
        'Amount (₵)',
        validators=[DataRequired(message="Amount is required.")]
    )
    category = StringField(
        'Category',
        validators=[DataRequired(message="Category is required.")]
    )
    type = SelectField(
        'Type',
        choices=[('Income', 'Income'), ('Expense', 'Expense')],
        validators=[DataRequired(message="Please select a type.")]
    )
    date = DateField(
        'Date',
        validators=[DataRequired(message="Date is required.")]
    )
    submit = SubmitField('Add Transaction')
