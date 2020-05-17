from unittest import TestCase, main

from app import db, create_app
from app.models import User

app = create_app(environment='testing')


class TestApp(TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.app_ctx = app.app_context()
        self.app_ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()

    def register(self, user_name, password='password'):
        user = User(name=user_name, password=password, activated=True)
        user.save()

    def login(self, user_name, password='password'):
        return self.client.post(
            '/login', data=dict(user_name=user_name, password=password),
            follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_index_page(self):
        # register test user.
        self.register('sam')
        # Login by test user
        response = self.login('sam')
        self.assertIn(b'Login successful.', response.data)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_login_and_logout(self):
        # Access to logout view before login should fail.
        response = self.logout()
        self.assertIn(b'Please log in to access this page.', response.data)
        # register test user.
        self.register('sam')
        # Login by test user
        response = self.login('sam')
        self.assertIn(b'Login successful.', response.data)
        # Should successfully logout the currently logged in user.
        response = self.logout()
        self.assertIn(b'You were logged out.', response.data)
        # Incorrect login credentials should fail.
        response = self.login('sam', 'wrongpassword')
        self.assertIn(b'Wrong user name or password.', response.data)
        # Correct credentials should login
        response = self.login('sam')
        self.assertIn(b'Login successful.', response.data)


if __name__ == "__main__":
    main()
