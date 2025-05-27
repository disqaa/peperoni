from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import datetime

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DeliveryForm(FlaskForm):
    address = StringField('Адрес', validators=[DataRequired()])
    delivery_time = DateTimeLocalField('Время доставки', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Оформить заказ')

    def validate_delivery_time(self, field):
        now = datetime.now().replace(second=0, microsecond=0)
        if field.data < now:
            raise ValidationError('Время доставки не может быть в прошлом.')
