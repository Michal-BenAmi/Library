import unittest
import json

import requests
from app.api import library_apis


class BookTestCase(unittest.TestCase):
    def setUp(self):
        self.app = library_apis.app.test_client()
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.auth = ('Joni Levy', 'JoniLevy123')
        self.auth_admin = ('Rivka Gim', 'RivkaGim12345')

    def test_add_book(self):
        # Test to add a book
        book = {
            'title': 'Lord of the Flies',
            'author': 'William Golding'
        }
        # send a POST request to the add_book endpoint with the book data - regular user
        response = self.app.post('http://localhost:5000/api/books', data=json.dumps(book), headers=self.headers, auth=self.auth)
        print(response.text)

        # check that the response status code is 401 - Unauthorized access. Admin rights required
        self.assertEqual(response.status_code, 401)

        # send a POST request to the add_book endpoint with the book data - admin user
        response = self.app.post('http://localhost:5000/api/books', data=json.dumps(book), headers=self.headers, auth=self.auth_admin)
        print(response.text)

        # check that the response status code is 201 (created)
        self.assertEqual(response.status_code, 201)

        # check that the response data contains the added book
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['title'], book['title'])
        self.assertEqual(data['author'], book['author'])

    def test_add_multiple_books(self):
        # Test to allow admin add multiple books
        # Arrange
        books = [
            {'title': 'Harry Potter1', 'author': 'J K Rowling'},
            {'title': 'Harry Potter2', 'author': 'J K Rowling'},
            {'title': 'Jane Eyre', 'author': 'Charlotte Bronte'},
            {'title': 'Catch-22', 'author': 'Joseph Heller'},
        ]

        # Act
        for book in books:
            response = self.app.post('http://localhost:5000/api/books', data=json.dumps(book), headers=self.headers, auth=self.auth_admin)
            print(response)
            print(response.request.url)
            print(response.text)
            print(response.request.url)

            # Assert
            self.assertEqual(response.status_code, 201)
            self.assertIn(book['title'], response.get_data(as_text=True))
            self.assertIn(book['author'], response.get_data(as_text=True))

    def test_get_books_with_filters(self):
        # Test getting books filtered by author name
        response = requests.get('http://localhost:5000/api/books', params={'author': 'J K Rowling'})
        print(response.url)
        print(response.text)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertGreater(len(data), 0)
        for book in data:
            self.assertEqual(book['author'], 'J K Rowling')

        # Test getting books filtered by title
        response = requests.get('http://localhost:5000/api/books', params={'title': 'Jane Eyre'})
        print(response.url)
        print(response.text)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertGreater(len(data), 0)
        for book in data:
            self.assertEqual(book['title'], 'Jane Eyre')

        # Test getting books filtered by availability
        response = requests.get('http://localhost:5000/api/books', params={'is_available': True})
        print(response.url)
        print(response.text)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertGreater(len(data), 0)
        for book in data:
            self.assertTrue(book['is_available'])


if __name__ == '__main__':
    unittest.main()
