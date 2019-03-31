from ..models import User
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Regexp, EqualTo


class EditProfileForm(FlaskForm):
    """
    Form for user to edit their profile
    """
    username = StringField('Username', validators=[DataRequired(), Length(1, 32), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    user_image = FileField('Add Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Profile')

    ##
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken')


class ChangePasswordForm(FlaskForm):
    """
    Form to change password
    """
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password', message='Your new password did not match')])
    submit = SubmitField('Update Password')


class ResetRequestForm(FlaskForm):
    """
    Form to request a password reset
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    # email validator method
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email not found!')


class ResetPasswordForm(FlaskForm):
    """
    Form to reset a new password
    """
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class ContactAdminForm(FlaskForm):
    """
    Form for users to contact Admin
    """
    message = TextAreaField('Message')
    submit = SubmitField('Submit')
