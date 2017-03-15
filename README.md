# weather_app
Simple Flask app for collecting weather info

# Deployment
Development environment setup instructions.

1. Set environment variables:

Examples:

export SECRET_KEY='hard to guess string'
export WEATHER_APP_DEV_DB='postgresql://user:pass@localhost/weather_app'
export WEATHER_APP_TEST_DB='postgresql://user:pass@localhost/weather_app' //needed to run unittests

export OWM_API_KEY='cc17b174ba934a330313e87ac5c5597b' //weather API key, copy it

// Gmail account credentials used for registration, password reset, email change.
// If ommited, user accounts will get confirmed automatically but password reset and email change will not work.
export MAIL_USERNAME='username@gmail.com'
export MAIL_PASSWORD='password'

2. pip install -r requirements/development.txt
3. python manage.py deploy
4. Done! Visit: http://localhost:5000
