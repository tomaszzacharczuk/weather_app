from flask import render_template, redirect, url_for, request, flash, Markup, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import login_user, login_required, logout_user, current_user
from .forms import LoginForm, RegistrationForm, PasswordResetForm, PasswordResetRequestForm, \
    ChangePasswordForm, ChangeEmailForm
from . import auth
from ..models import User, Role
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('User with given email does not exist.')
            return redirect(url_for('auth.login'))
        if not user.confirmed:
            link = '<a href="' + url_for('auth.resend_confirmation', email=form.email.data) + '">resend</a>'
            flash(Markup(
                'Your account is not confirmed. Please check your email addres and confirm your account '
                'before you login. You can also ' + link + ' email confirmation for ' + form.email.data))
            return redirect(url_for('auth.login'))
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        role = Role.query.filter_by(name="User").first()
        user = User(email=form.email.data, password=form.password.data, role=role)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            'Confirm Your Account',
            'auth/email/confirm',
            user=user,
            token=token)
        flash('Confirmation email has been sent to your email address')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
def confirm(token):
    # if user is logged in, it means that he's already confirmed. Redirect!
    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('main.index'))
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('main.index'))
    user = User.query.filter_by(id=data.get('confirm')).first()
    if user:
        user.confirmed = True
        db.session.add(user)
        flash('You have confirmed your account. You can login now.')
        return redirect(url_for('auth.login'))
    else:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('main.index'))


@auth.route('/confirm/resend/<email>')
def resend_confirmation(email):
    user = User.query.filter_by(email=email).first()
    if user:
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            'Confirm Your Account',
            'auth/email/confirm',
            user=user,
            token=token)
        flash('Confirmation email has been resend.')
    else:
        flash('User with given email does not exist.')
    return redirect(url_for('auth.login'))


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
