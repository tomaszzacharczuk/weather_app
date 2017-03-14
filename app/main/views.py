from flask import render_template
from flask_login import current_user, login_required
from . import main
from ..models import User, Location, Weather


@main.route('/')
def index():
    user_count = User.query.count()
    location_count = Location.query.count()
    weather_count = Weather.query.count()
    return render_template('index.html',
                           user_count=user_count,
                           weather_count=weather_count,
                           location_count=location_count)


@main.route('/dashboard')
@login_required
def dashboard():
    locations = current_user.locations.all()
    return render_template('dashboard.html', locations=locations)