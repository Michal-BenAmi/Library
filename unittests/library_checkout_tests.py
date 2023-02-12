import unittest
import json
from src import library_db


class CheckoutTestCase(unittest.TestCase):
    def setUp(self):
        # Create test client
        self.app = library_db.app.test_client()
        # self.client = app.test_client
        self.headers = {
            'Content-Type': 'application/json'
        }


    def test_checkout_api(self):
        # data to be sent to api
        data = {
            "book_id": 2,
            "user_id": 6
        }

        # sending post request and saving response as response object
        response = self.app.post("/api/checkout", headers=self.headers, data=json.dumps(data))

        # assert the status code of the response is 201 (Created)
        assert response.status_code == 201

        # retrieve the response data as a dictionary
        response_data = json.loads(response.text)
        print('response.text')
        print(response.text)

        # assert that the response contains the expected data
        assert response_data['id'] == 2
        assert response_data['user_id'] == 2

    def test_checkout_with_valid_data(self):
        # Send a POST request to the API with valid data
        response = self.app.post('/api/checkout', data={'book_id': 1})
        print(response)

        # Check that the response has a 201 status code
        self.assertEqual(response.status_code, 201)

        # Parse the response data as JSON
        data = json.loads(response.data)

        # Check that the response data contains the expected values
        self.assertIn('book_id', data)
        self.assertIn('status', data)
        self.assertEqual(data['book_id'], 1)
        self.assertEqual(data['status'], 'checked out')

    def test_checkout_with_invalid_book_id(self):
        # Send a POST request to the API with an invalid book_id
        response = self.app.post('/api/checkout', data={'book_id': 999})

        # Check that the response has a 400 status code
        self.assertEqual(response.status_code, 400)

        # Check that the response data contains an error message
        self.assertIn('error', response.data)

if __name__ == '__main__':
    unittest.main()