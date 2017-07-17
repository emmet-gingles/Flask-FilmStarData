import recommender
import unittest

# class to test recommender client requests
class TestRecommender(unittest.TestCase):

    # setup for testing client requests. Called at the start of each test
    def setUp(self):
        self.app = recommender.app.test_client()
        self.app.testing = True

    # called at the end of each test
    def tearDown(self):
        pass

    # test for the index decorator to ensure that it is accessible from its URL
    def test_index(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    # test for the attrbute decorator to ensure that it is accessible from its URL
    def test_attribute(self):
        result = self.app.get('/attribute/')
        self.assertEquals(result.status_code, 200)

    # test for the tool decorator to ensure that it is accessible from its URL
    def test_tool(self):
        result = self.app.get('/tool/')
        self.assertEquals(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()