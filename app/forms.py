from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeLocalField, SelectMultipleField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from datetime import datetime
from wtforms.widgets import ListWidget, CheckboxInput



class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    favorite_categories = SelectMultipleField(
        'Любимые категории пиццы',
        choices=[
            ('мясная', 'Мясная'),
            ('сырная', 'Сырная'),
            ('веган', 'Веган'),
            ('морепродукты', 'Морепродукты'),
            ('острая', 'Острая')
        ],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput()
    )
    submit = SubmitField('Зарегистрироваться')

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


class ReviewForm(FlaskForm):
    rating = SelectField("Оценка", choices=[(str(i), f"{i} звёзд") for i in range(1, 6)], validators=[DataRequired()])
    text = TextAreaField("Комментарий", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Оставить отзыв")