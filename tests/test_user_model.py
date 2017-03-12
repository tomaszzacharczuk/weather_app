from unittest import TestCase
from app.models import User


class UserModelTestCase(TestCase):
    def test_password(self):
        u = User(password="shelby")
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password="shelby123")
        with self.assertRaises(AttributeError):
            print(u.password)

    def test_password_verification(self):
        u = User(password="shelby321")
        self.assertTrue(u.verify_password("shelby321"))
        self.assertFalse(u.verify_password("shelby123"))

    def test_salts_are_random(self):
        u1 = User(password="shelby")
        u2 = User(password="shelby")
        self.assertTrue(u1.password_hash != u2.password_hash)
