from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    name = StringField('Nome Completo', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    role = StringField('Cargo', validators=[DataRequired()])
    turno = StringField('Turno', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

class DeviceForm(FlaskForm):
    name = StringField('Nome do Dispositivo', validators=[DataRequired()])
    type = StringField('Tipo de Dispositivo', validators=[DataRequired()])
    submit = SubmitField('Adicionar Dispositivo')

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class LogoutForm(FlaskForm):
    submit = SubmitField('Sair')

