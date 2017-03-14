from flask import render_template
from flask_login import current_user, login_required
from . import main


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    locations = current_user.locations.all()
    return render_template('dashboard.html', locations=locations)