import unittest
import json

from app.api import library_apis


class TestRegisterAPI(unittest.TestCase):
    def setUp(self):
        self.app = library_apis.app.test_client()
        self.headers = {
            'Content-Type': 'application/json'
        }

    def test_users_register_api(self):
        user = {
            "username": "Shiri Cohen",
            "email": "ShiriCohen@gmail.com",
            "password": "Shiricohen123"
        }

        # Send a POST request to the API with the user data
        response = self.app.post("http://localhost:5000/api/users", headers=self.headers, data=json.dumps(user))

        # Check that the API returns a 201 status code, indicating that the user has been successfully registered
        self.assertEqual(response.status_code, 201)

        # Check that the API returns a JSON object containing the user's information
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.json, {'message': 'User created successfully'})

    def test_users_register_multiple_users(self):
        users = [
            {
                "username": "Joni Levy",
                "email": "JoniLevy@example.com2",
                "password": "JoniLevy123"
            },
            {
                "username": "Sara Shos",
                "email": "SaraShos@yahho.com",
                "password": "S!saraShos123"
            },
            {
                "username": "Rivka Gim",
                "email": "RivkaGim@gmail.com",
                "password": "RivkaGim12345",
                "is_admin": True
            },
            {
                "username": "Rachel Ru",
                "email": "RachelRu@yahho.com",
                "password": "Rachel!!Ru123"
            },
            {
                "username": "Shimon Bor",
                "email": "Shimon_Boru@gmail.com",
                "password": "ShimonBor!123"
            }
        ]

        for user in users:
            # Send a POST request to the API with the user data
            response = self.app.post("http://localhost:5000/api/users", headers=self.headers, data=json.dumps(user))

            # Check that the API returns a 201 status code, indicating that the user has been successfully registered
            self.assertEqual(response.status_code, 201)

            # Check that the API returns a JSON object containing the user's information
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(response.json, {'message': 'User created successfully'})

    def test_register_existing_user(self):
        user = {
            "username": "test_user4",
            "email": "test_user4@example.com",
            "password": "test_password4"
        }

        # Send a POST request to the API with the user data
        self.app.post("http://localhost:5000/api/users", headers=self.headers, data=json.dumps(user))

        # Try to register the same user again
        response = self.app.post("http://localhost:5000/api/users", headers=self.headers, data=json.dumps(user))

        # Check that the API returns a 500 status code, indicating that the user already exists
        self.assertEqual(response.status_code, 500)

    def test_register_invalid_data(self):
        user = {
            "username": "test_user55",
            "password": "test_password5"
        }

        # Try to register a user with missing information
        response = self.app.post("http://localhost:5000/api/users", headers=self.headers, data=json.dumps(user))

        # Check that the API returns
        self.assertEqual(response.status_code, 400)

    def test_register_invalid_email_data(self):
        user = {
            "username": "test_user5",
            "password": "test_password5",
            "email": "test_user5example.com@",
        }

        # Try to register a user with missing information
        response = self.app.post("http://localhost:5000/api/users", headers=self.headers, data=json.dumps(user))

        # Check that the API returns
        self.assertEqual(response.status_code, 400)

    def test_delete_user_by_regular_user(self):
        # Test deleting user by regular user
        auth = ('Joni Levy', 'JoniLevy123')
        response = self.app.delete('/api/users/2', headers=self.headers, auth=auth)
        # Unauthorized Access
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
