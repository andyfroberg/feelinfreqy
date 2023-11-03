from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, TextAreaField, EmailField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Email(), Length(min=5, max=50)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=5, max=50)])

class RegisterForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Email(), Length(min=5, max=50)])
    username = StringField('username', validators=[DataRequired(), Length(min=5, max=50)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=5, max=50)])
    confirmPassword = PasswordField('confirmPassword', validators=[DataRequired(), EqualTo('password'), Length(min=5, max=50)])
    
class PasswordChangeForm(FlaskForm):
    newPassword = PasswordField('newPassword', validators=[DataRequired(), Length(min=5, max=50)])
    confirmNewPassword = PasswordField('confirmNewPassword', validators=[DataRequired(), EqualTo('newPassword'), Length(min=5, max=50)])

class TriviaAnswerForm(FlaskForm):
    answer = StringField('answer', validators=[DataRequired(), Length(min=1, max=50)])

class UserFilterForm(FlaskForm):
    query = StringField('query', validators=[Length(min=0, max=50)])


class CreatePlaylist(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=1, max=64)])
    mood = StringField('mood', validators=[DataRequired(), Length(min=1, max=64)])

class CreateSong(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(min=1, max=64)])
    artist = StringField('artist', validators=[DataRequired(), Length(min=1, max=64)])
