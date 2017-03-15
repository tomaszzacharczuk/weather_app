import atexit
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import pyowm
from manage import app
from .. import db
from ..models import Location, Weather


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


def collect_weather():
    # Just for debugging only
    print_date_time()
    with app.app_context():
        owm = pyowm.OWM(app.config['OWM_API_KEY'])
        locations = Location.query.all()
        # TODO: Instead of loop, use bulk pull by city ID from API
        for location in locations:
            w = owm.weather_at_place(location.name).get_weather()
            temperature = w.get_temperature('celsius')
            wind = w.get_wind()
            weather = Weather(
                temperature=temperature['temp'],
                temperature_min=temperature['temp_min'],
                temperature_max=temperature['temp_max'],
                wind=wind['speed'],
                date=datetime.utcfromtimestamp(w.get_reference_time()),
                location=location
            )
            db.session.add(weather)


# I used to use CRON jobs for that kind of tasks in PHP,
# probably Celery would be better solution in Python
# although it seemed like overkill for this task
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=collect_weather,
    trigger=IntervalTrigger(minutes=5),
    id='collect_weather',
    name='Collect weather every half an hour',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
