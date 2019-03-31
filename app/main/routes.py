from datetime import datetime
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from . import main
from .forms import LoginForm, ChangePasswordForm
from .. import database
from ..models import User, Sample, Patient, Clinic
from ..utils import send_email


@main.before_app_request
def before_request():
    """
    When user is logged in, record/update user visit//
    Redirects url if the user account is not activated
    """
    if current_user.is_authenticated:
        current_user.last_visit = datetime.utcnow()
        database.commit()
        if not current_user.account_confirmed and request.endpoint and request.blueprint != 'main' and request.endpoint != 'static':
            return redirect(url_for('main.unconfirmed'))


@main.route("/index")
@main.route("/")
@login_required
def index():
    if not current_user.account_confirmed:
        return redirect(url_for('main.unconfirmed'))
    else:
        patients = Patient.query.count()
        samples = Sample.query.count()
        users = User.query.count()
        clinics = Clinic.query.count()
        return render_template('index.html', total_patients=patients,
                               total_samples=samples, total_users=users, total_clinics=clinics)


@main.route('/unconfirmed')
def unconfirmed():
    if current_user.account_confirmed:
        return redirect(url_for('main.index'))
    return render_template('/main/unconfirmed.html')


@main.route('/confirm/<token>', methods=['GET', 'POST'])
@login_required
def confirm(token):
    """
    Handle request to url /confirm/<token>
    Allows user to activate the account and change passward after first login
    """
    if current_user.account_confirmed:
        flash('Your account was previously confirmed', 'info')
        return redirect(url_for('main.index'))

    if current_user.verify_new_user_token(token):
        form = ChangePasswordForm()
        if request.method == 'GET':
            flash('Please change your password to confirm account', 'success')

        if form.validate_on_submit():
            if current_user.verify_password(form.old_password.data):
                current_user.password = form.password.data
                database.update(current_user)
                # db.session.add(current_user)
                # db.session.commit()
                flash('Your account is activated and password has been updated.', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Invalid, old password did not match', 'danger')

    else:
        flash('Confirmation Link expired, Please request new link', 'danger')
        return redirect(url_for('main.unconfirmed'))
    return render_template('/users/change_password.html', form=form)


@main.route('/confirm')
@login_required
def not_confirmed():
    """
    Route to send new confirmation email to user
    """
    if not current_user.account_confirmed:
        token = current_user.get_new_user_token()
        send_email(current_user.email,
                   'Confirm Your Account',
                   'users/email/confirm',
                   user=current_user,
                   token=token)
        flash('New Confirmation link has been sent to your email', 'info')
    return redirect(url_for('main.index'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to url route /login
    Log a user using login Form
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Invalid email or password, Please try again', 'danger')
    return render_template('/main/login.html', form=form)


@main.route('/logout')
def logout():
    """
    Handle requests to url route /logout
    Log a user out
    """
    logout_user()
    return redirect(url_for('main.index'))
