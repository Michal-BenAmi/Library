import unittest

# Load all the tests from the test files
register_tests = unittest.TestLoader().discover('.', pattern='library_users_tests.py')
books_tests = unittest.TestLoader().discover('.', pattern='library_books_tests.py')
checkout_tests = unittest.TestLoader().discover('.', pattern='library_checkout_tests.py')

# Create a test suite from all the tests
suite = unittest.TestSuite([register_tests, books_tests, checkout_tests])

def run_tests():
    # Run the test suite
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    run_tests()
