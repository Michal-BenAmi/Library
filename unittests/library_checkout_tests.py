import unittest
import json
from src import library_db_apis


class CheckoutTestCase(unittest.TestCase):
    def setUp(self):
        # Create test client
        self.app = library_db_apis.app.test_client()
        self.headers = {
            'Content-Type': 'application/json'
        }

    def test_checkout_api(self):
        # data to be sent to api
        data = {
            "book_id": 48,
            "user_id": 31
        }

        # sending post request and saving response as response object
        response = self.app.post("http://localhost:5000/api/checkout", headers=self.headers, data=json.dumps(data))

        # assert the status code of the response is 201 (Created)
        assert response.status_code == 201

        # retrieve the response data as a dictionary
        response_data = json.loads(response.text)
        print(response.text)

        # assert that the response contains the expected data
        assert response_data['book_id'] == 48
        assert response_data['user_id'] == 31

    def test_checkout_checkouted_book(self):
        # data to be sent to api
        data = {
            "book_id": 50,
            "user_id": 32
        }

        # sending post request and saving response as response object
        response = self.app.post("http://localhost:5000/api/checkout", headers=self.headers, data=json.dumps(data))

        # assert the status code of the response is 201 (Created)
        assert response.status_code == 201

        # resending post request and saving response as response object
        response = self.app.post("http://localhost:5000/api/checkout", headers=self.headers, data=json.dumps(data))

        # assert the status code of the response is 500 (Book is not available)
        assert response.status_code == 500

    def test_checkout_with_invalid_book_id(self):
        # Send a POST request to the API with an invalid book_id
        response = self.app.post('http://localhost:5000/api/checkout', data={'book_id': 999})

        # Check that the response has a 400 status code
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
