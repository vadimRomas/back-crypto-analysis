from django.test import TestCase

# Create your tests here.


class TestMyPayments(TestCase):

    def setUp(self):
        print('START!')

    def test_checkout(self):
        test_url = "my_payments/checkout"
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)
