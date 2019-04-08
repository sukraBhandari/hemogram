from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_required

from . import users
from .forms import EditProfileForm, ChangePasswordForm, ResetRequestForm, ResetPasswordForm,\
    ContactAdminForm
from .. import database
from ..models import User
from ..utils import send_email, save_image, upload_file_to_s3


@users.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Handle requests to url /edit_profile
    Allows logged in user to edit profile
    """
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        if form.user_image.data:
            image_file = upload_file_to_s3(form.user_image.data, "profile_images")
            current_user.profile_image = image_file
        # db.session.add(current_user._get_current_object())
        # db.session.commit()
        database.update(current_user._get_current_object())
        flash('Your Profile has been updated!', 'success')
        return redirect(url_for('users.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    picture_file = url_for('static', filename='images/profile_img/' + current_user.profile_image)
    return render_template('users/edit_profile.html', form=form,
                           image_file=picture_file)


@users.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Handle requests to url /change_password
    Allows user to change password
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            # db.session.add(current_user)
            # db.session.commit()
            database.update(current_user)
            flash('Your password has been updated.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Your old password is incorrect', 'danger')
    return render_template('users/change_password.html', form=form)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    """
    Handle request to url /reset_password
    Allows user to send a request to reset their old password
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_password_reset_token()
            send_email(user.email, 'Please, Reset Your Password',
                       'users/email/reset_password',
                       user=user,
                       token=token)
            flash('Please check your email to reset your password', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('No email found', 'danger')
    return render_template('users/password_reset_request.html', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    """
    Handle request to url /reset_password/<token>
    Allows user to reset password as long as token is still valid
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.verify_password_reset_token(token, form.password.data):
            database.commit()
            flash('Your password has been reset.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid token', 'danger')
            return redirect(url_for('users.reset_password_request'))
    return render_template('/users/reset_password.html', form=form)


@users.route('/users')
@login_required
def all_users():
    """
    Handle request to url /users
    Allows to excess all users info
    """
    users = User.query.order_by(User.id.desc()).all()
    return render_template('/users/users.html', users=users)


@users.route('/profile')
@login_required
def profile():
    """
    Route to display user profile
    """
    return render_template('users/profile.html')


@users.route('/contact_admin', methods=['GET', 'POST'])
@login_required
def contact():
    """
    Route to display form to send message to admin
    TODO
    """
    form = ContactAdminForm()
    if form.validate_on_submit():
        pass
    return render_template('users/contact_admin.html', form=form)
