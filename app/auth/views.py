from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from .forms import LoginForm, RegistrationForm
from . import auth
from ..models import User, Role
from .. import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for(request.args.get('next') or url_for('main.index')))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        role = Role.query.filter_by(name="User").first()
        user = User(email=form.email.data, password=form.password.data, role=role)
        db.session.add(user)
        flash('You can login now')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
