from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from ..models import User, Role


class AddUser(FlaskForm):
    """
    Form for administrator to add new Lab users
    """
    f_name = StringField('First Name', validators=[DataRequired(), Length(1, 64)])
    l_name = StringField('Last Name', validators=[DataRequired(), Length(1, 64)])
    title = StringField('Job Title', validators=[DataRequired()])
    email = StringField('User Email', validators=[DataRequired(), Email()])
    confirm_email = StringField('Confirm User Email', validators=[DataRequired(), Email(), EqualTo('email')])
    submit = SubmitField('Register')

    # validate user email does not exists in db

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use!')


class UserProfileUpdate(FlaskForm):
    """
    Form to update user profile informaton
    """
    username = StringField('Username', validators=[DataRequired(), Length(1, 32),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    f_name = StringField('First Name', validators=[DataRequired(), Length(1, 64)])
    l_name = StringField('Last Name', validators=[DataRequired(), Length(1, 64)])
    title = StringField('Job Title', validators=[DataRequired()])
    email = StringField('User Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        """
        constructor method
        instantiate the role selectfield with choices
        """
        super(UserProfileUpdate, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        """
        Validate function to confirm unique email address
        """
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """
        validate function to confirm unique username
        """
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is taken.')
