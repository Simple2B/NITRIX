from unittest import TestCase, main

from app import db, create_app

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

    def login(self, user_id, password='password'):
        return self.client.post(
            '/login', data=dict(user_id=user_id, password=password),
            follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    main()
