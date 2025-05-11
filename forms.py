from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, message="Username must be at least 3 characters.")
    ])
    email = StringField('Email', validators=[
        DataRequired(), Email(message="Enter a valid email.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6, message="Password must be at least 6 characters.")
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), Email(message="Enter a valid email.")
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TransactionForm(FlaskForm):
    amount = FloatField('Amount (₵)', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    type = SelectField('Type', choices=[
        ('Income', 'Income'), ('Expense', 'Expense')
    ], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Add Transaction')
