from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DeliveryForm(FlaskForm):
    delivery_time = DateTimeField(
        'Preferred delivery time (YYYY-MM-DD HH:MM)',
        format='%Y-%m-%d %H:%M',
        validators=[DataRequired()]
    )
    submit = SubmitField('Place order')
