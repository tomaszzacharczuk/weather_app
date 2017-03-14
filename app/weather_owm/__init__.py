from flask import Blueprint

weather_owm = Blueprint('weather_owm', __name__)

from . import views, scheduler