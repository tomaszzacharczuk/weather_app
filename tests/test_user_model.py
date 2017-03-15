from unittest import TestCase
from app.models import User, Role
from app import create_app, db


class UserModelTestCase(TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user_role = Role(name="User")
        self.admin_role = Role(name="Administrator")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

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

    def test_username_getter(self):
        u = User(email="user@email.com")
        self.assertEqual("user", u.username)

    def test_valid_confirmation_token(self):
        u = User(email="user@example.com", password="123", role=self.user_role)
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(email="user@example.com", password="123", role=self.user_role)
        u2 = User(email="user2@example.com", password="123", role=self.user_role)
        db.session.add_all([u1, u2])
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_password_reset(self):
        u = User(email="user@example.com", password="123", role=self.user_role)
        u2 = User(email="user2@example.com", password="123", role=self.user_role)
        db.session.add_all([u, u2])
        db.session.commit()
        token = u.generate_reset_token()
        token2 = u2.generate_reset_token()
        self.assertTrue(u.reset_password(token, '321'))
        # wrong token from another user
        self.assertFalse(u.reset_password(token2, '321'))
        db.session.commit()
        # new password
        self.assertTrue(u.verify_password('321'))
        # old password
        self.assertFalse(u.verify_password('123'))

    def test_change_email(self):
        u = User(email="user@example.com", password="123", role=self.user_role)
        token = u.generate_email_change_token('new_email@example.com')
        self.assertTrue(u.change_email(token))
        db.session.commit()
        self.assertEqual('new_email@example.com', u.email)

    def test_change_invalid_email(self):
        # empty email
        u = User(email="user@example.com", password="123", role=self.user_role)
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token(None)
        self.assertFalse(u.change_email(token))

        # wrong token
        self.assertFalse(u.change_email('123'))

        # email already exists
        u1 = User(email="user1@example.com", password="123", role=self.user_role)
        u2 = User(email="user2@example.com", password="123", role=self.user_role)
        token = u1.generate_email_change_token(u2.email)
        self.assertFalse(u2.change_email(token))