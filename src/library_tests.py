import unittest
import json

from src import library_db


class BookTestCase(unittest.TestCase):
    def setUp(self):
        self.app = library_db.app.test_client()
        self.book = {
            'title': 'Test Book',
            'author': 'Test Author'
        }

    def test_add_book(self):
        # send a POST request to the add_book endpoint with the book data
        response = self.app.post('/api/books', data=json.dumps(self.book), content_type='application/json')

        # check that the response status code is 201 (created)
        self.assertEqual(response.status_code, 201)

        # check that the response data contains the added book
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['title'], self.book['title'])
        self.assertEqual(data['author'], self.book['author'])

    def test_add_multiple_books(self):
        # Arrange
        books = [
            {'title': 'Harry Potter', 'author': 'J. K. Rowling'},
            {'title': 'Jane Eyre', 'author': 'Charlotte Bronte'},
            {'title': 'Catch-22', 'author': 'Joseph Heller'},
        ]

        # Act
        for book in books:
            response = self.app.post('/api/books', data=json.dumps(book), content_type='application/json')

            # Assert
            self.assertEqual(response.status_code, 201)
            self.assertIn(book['title'], response.get_data(as_text=True))
            self.assertIn(book['author'], response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
