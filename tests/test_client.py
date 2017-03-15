from unittest import TestCase
import re
from flask import url_for
from app import create_app, db
from app.models import User, Role


class WeatherAppClientTestCase(TestCase):
    def setUp(self):
        # create app context
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        # create test DB
        db.create_all()
        # set client
        self.client = self.app.test_client(use_cookies=True)
        Role.initiate()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue(b'Hello, Stranger!' in response.data)

    def test_register_login(self):
        # register
        response = self.client.post(url_for('auth.register'), data={
            'email': 'tom@example.com',
            'password': 'tom',
            'confirm_password': 'tom'
        })
        self.assertTrue(response.status_code == 302)

        user = User.query.filter_by(email='tom@example.com').first()
        self.assertIsNotNone(user)
        self.assertFalse(user.confirmed)

        # try to login
        response = self.client.post(url_for('auth.login'), data={
            'email': 'tom@example.com',
            'password': 'tom'
        }, follow_redirects=True)
        self.assertTrue(b'Your account is not confirmed.' in response.data)

        # confirm account
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)
        self.assertTrue(b'You have confirmed your account. You can login now.', response.data)

        # login
        response = self.client.post(url_for('auth.login'), data={
            'email': 'tom@example.com',
            'password': 'tom'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search('Hello,\s+tom!', data))

        # redirect already loggedin user
        response = self.client.post(url_for('auth.login'), data={
            'email': 'tom@example.com',
            'password': 'tom'
        })
        self.assertTrue(response.status_code, 302)


        # logout
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        self.assertTrue(b'You have been logged out.', response.data)
