from django.test import TestCase

# Create your tests here.


class UserTests(TestCase):

    def setUp(self):
        print('START!')

    def test_create_user(self):
        test_url = 'user/register'
        response = self.client.post(test_url, {"email": "email@q.com", "password": "password"})
        self.assertEqual(response.status_code, 201)

    def test_fail_create_user(self):
        test_url = 'user/register'
        response = self.client.post(test_url, {"email": "email@q.com", "password": "password"})
        self.assertEqual(response.status_code, 400)

    def test_login(self):
        test_url = 'user/login'
        data = {"email": "email@q.com", "password": "password"}
        response = self.client.post(test_url, data)
        self.assertEqual(response.status_code, 200)

    def test_fail_login(self):
        test_url = 'user/login'
        data = {"email": "email@q.com"}
        response = self.client.post(test_url, data)
        self.assertEqual(response.status_code, 400)

    def test_get_user(self):
        test_url = 'user/'
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

    def test_fail_get_user(self):
        test_url = 'user/'
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

    def test_get_user_not_authorization(self):
        test_url = 'user/'
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 401)

    def test_update_user(self):
        test_url = 'user/'
        data = {"first_name": "Vadym", "last_name": "Romas", "email": "email@q.com"}
        response = self.client.put(test_url, data)
        self.assertEqual(response.status_code, 200)

    def test_fail_update_user(self):
        test_url = 'user/'
        data = {"first_name": "Vadym", "last_name": "Romas"}
        response = self.client.put(test_url, data)
        self.assertEqual(response.status_code, 400)

    def test_delete_user(self):
        test_url = 'user/'
        response = self.client.delete(test_url)
        self.assertEqual(response.status_code, 204)

    def test_fail_delete_user(self):
        test_url = 'user/'
        response = self.client.delete(test_url)
        self.assertEqual(response.status_code, 404)
