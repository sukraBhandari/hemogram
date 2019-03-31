import os
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import admin
from .forms import AddUser, UserProfileUpdate
from ..models import User, Role
from .. import database
from ..utils import send_email, admin_required, random_string


@admin.route('/')
@login_required
@admin_required
def admin_home():
    return '<h1>Hello Admin</h1>'


@admin.route("/users/add", methods=['GET', 'POST'])
@login_required
@admin_required
def register():
    """
    Handle requests to the /admin/users/add
    Allows admin to register new user
    """
    form = AddUser()

    if form.validate_on_submit():
        temp_pass = random_string()
        user = User(user_first_name=form.f_name.data,
                    user_last_name=form.l_name.data,
                    email=form.email.data,
                    password=temp_pass)
        # add user to the db
        database.create(user)
        # add following functionality
        # 1. generate account confirmation token with time limit
        token = user.get_new_user_token()
        # 2. email user to confirm their new account
        send_email(user.email,
                   'Verify Your Account',
                   'admin/email/add_lab_user',
                   user=user,
                   token=token,
                   temp_pass=temp_pass)
        flash('New Lab user has been added successfully!', 'success')

        # redirect to the main page
        return redirect(url_for('main.index'))

    # load the admin registration template
    return render_template('admin/add_user.html', form=form)


@admin.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """
    Handle request to edit user information
    by administarion.
    """
    user = User.query.get_or_404(id)
    form = UserProfileUpdate(user=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.f_name = form.f_name.data
        user.l_name = form.l_name.data
        user.email = form.email.data
        user.title = form.title.data
        user.role = Role.query.get(form.role.data)
        database.update(user)
        ###
        # TODO - Send user an email with update
        ###
        flash('User Profile has been updated!', 'success')
        return redirect(url_for('admin.edit_user', id=user.id))
    elif request.method == 'GET':
        form.username.data = user.username
        form.f_name.data = user.user_first_name
        form.l_name.data = user.user_last_name
        form.email.data = user.email
        form.title.data = user.title
        form.role.data = user.role_id
    picture_file = url_for('static', filename='images/profile_img/' + user.profile_image)
    return render_template('admin/edit_user.html', form=form, user=user, image_file=picture_file, admin_email=os.environ.get('LAB_ADMIN'))


@admin.route('/users')
@login_required
@admin_required
def all_users():
    """
    Admin View - all users data
    """
    users = User.query.order_by(User.id.desc()).all()
    return render_template('/admin/users.html', users=users)


@admin.route('/users/<int:id>')
@login_required
def user_profile(id):
    """
    Admin view of individual user
    """
    user = User.query.get_or_404(id)
    return render_template('admin/user_profile.html', user=user)
