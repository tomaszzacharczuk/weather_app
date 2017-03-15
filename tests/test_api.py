from unittest import TestCase
from base64 import b64encode
import json
from flask import url_for
from app import create_app, db
from app.models import Role, User, Location


class APITestCase(TestCase):
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

    def get_user(self):
        user_role = Role.query.filter_by(name="User").first()
        user = User(email='user@example.com', password='user', role=user_role, confirmed=True)
        db.session.add(user)
        db.session.commit()
        return {'email': user.email, 'password': 'user'}

    def get_api_headers(self, email, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (email + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        response = self.client.get('/imaginary/url',
                                   headers=self.get_api_headers('email', 'password'))
        self.assertEqual(404, response.status_code)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual('not found', json_response['error'])

    def test_no_auth(self):
        response = self.client.get(url_for('api.get_locations'),
                                   content_type="application/json")
        self.assertEqual(401, response.status_code)

    def test_bad_auth(self):
        user = self.get_user()
        response = self.client.get(url_for('api.get_token'),
                                   headers=self.get_api_headers(user['email'], 'random_password'))
        self.assertEqual(401, response.status_code)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual('Invalid credentials', json_response['message'])

    def test_token_auth(self):
        # request with bad token
        response = self.client.get(url_for('api.get_locations'),
                                  headers=self.get_api_headers('bad token', ''))
        self.assertEqual(401, response.status_code)
        # request token
        user = self.get_user()
        response = self.client.get(url_for('api.get_token'),
                                   headers=self.get_api_headers(user['email'], user['password']))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response['token'])
        token = json_response['token']

        # request with correct token
        response = self.client.get(url_for('api.get_locations'),
                                   headers=self.get_api_headers(token, ''))
        self.assertEqual(200, response.status_code)

    def test_get_locations(self):
        # set locations
        user = self.get_user()
        location_names = ['New York', 'Los Angeles', 'Warsaw', 'Krakow']
        u = User.query.filter_by(email=user['email']).first()
        for name in location_names:
            l = Location(name=name)
            u.locations.append(l)
        db.session.add(u)
        db.session.commit()

        # get token
        response = self.client.get(url_for('api.get_token'),
                                   headers=self.get_api_headers(user['email'], user['password']))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response['token'])
        token = json_response['token']

        # get locations
        response = self.client.get(url_for('api.get_locations'),
                                   headers=self.get_api_headers(token, ''))
        self.assertEqual(200, response.status_code)
        json_response = json.loads(response.data.decode('utf-8'))
        location_names_from_api = [location['name'] for location in json_response['locations']]
        self.assertListEqual(location_names, location_names_from_api)
