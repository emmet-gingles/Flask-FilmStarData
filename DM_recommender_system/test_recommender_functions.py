import recommender
import unittest

# class to test the recommender functions
class TestRecommenderFunctions(unittest.TestCase):

    # setup test functions. Called at the start of each test
    def setUp(self):
        self.app = recommender
        self.app.testing = True

    # called at the end of each test
    def tearDown(self):
        pass

    # tests for splitString()
    def test_splitString(self):
        result = self.app.splitString('free=yes')
        self.assertEquals(result, (['free'],['yes']))
        result = self.app.splitString('free=yes&gui=no')
        self.assertEquals(result,(['free','gui'],['yes','no']))
        result = self.app.splitString('freeyes&guino')
        self.assertEquals(result, "ERROR: String must contain '='")

    # tests for readFile()
    def test_readFile(self):
        result = self.app.readFile('data/Data Mining Tools.xlsx')
        self.assertEquals(len(result), 10)
        result = self.app.readFile('data/Data Mining Tool Ratings.xlsx')
        self.assertEquals(len(result), 30)
        result = self.app.readFile(123)
        self.assertEquals(result, 'ERROR: First Parameter should be a string')
        result = self.app.readFile('data/Data.xlsx')
        self.assertEquals(result, 'ERROR: File not found')

    # tests for joinData()
    def test_joinData(self):
        file1 = self.app.readFile('data/Data Mining Tools.xlsx')
        file2 = self.app.readFile('data/Data Mining Tool Ratings.xlsx')
        result = self.app.joinData(file1, file2)
        self.assertEquals(len(result), 10)
        result = self.app.joinData('file1', file2)
        self.assertEquals(result, 'ERROR: First and second parameters should be data frames')
        result = self.app.joinData(file1, 'file2')
        self.assertEquals(result, 'ERROR: First and second parameters should be data frames')

    # tests for searchData()
    def test_searchData(self):
        file1 = self.app.readFile('data/Data Mining Tools.xlsx')
        file2 = self.app.readFile('data/Data Mining Tool Ratings.xlsx')
        data = self.app.joinData(file1, file2)
        result = self.app.searchData(data, (['Free']), (['yes']))
        self.assertEquals(len(result), 7)
        result = self.app.searchData(data, (['Free','Open_source']), (['yes','no']))
        self.assertEquals(len(result), 3)
        result = self.app.searchData('data', (['Free']), (['yes']))
        self.assertEquals(result, 'ERROR: First parameter should be a data frame')
        result = self.app.searchData(data, 'Free', (['yes']))
        self.assertEquals(result, 'ERROR: First and second parameters should be lists')
        result = self.app.searchData(data, (['Free']), 'yes')
        self.assertEquals(result, 'ERROR: First and second parameters should be lists')
        result = self.app.searchData(data, [], [])
        self.assertEquals(result, 'ERROR: List cannot contain no values')
        result = self.app.searchData(data, (['Free']), ([]))
        self.assertEquals(result, 'ERROR: Lists must be the same size')
        result = self.app.searchData(data, ([]), (['yes']))
        self.assertEquals(result, 'ERROR: Lists must be the same size')
        result = self.app.searchData(data, (['Free']), (['yes', 'no']))
        self.assertEquals(result, 'ERROR: Lists must be the same size')
        result = self.app.searchData(data, (['Free','Open_source']), (['yes']))
        self.assertEquals(result, 'ERROR: Lists must be the same size')

    # tests for selectTool()
    def test_selectTool(self):
        file1 = self.app.readFile('data/Data Mining Tools.xlsx')
        file2 = self.app.readFile('data/Data Mining Tool Ratings.xlsx')
        data = self.app.joinData(file1, file2)
        result = self.app.selectTool(data, 'R', True)
        self.assertEquals(len(result), 1)
        result = self.app.selectTool(data, 'R', False)
        self.assertEquals(len(result), 9)
        result = self.app.selectTool(data, 'R', 'True')
        self.assertEquals(result, 'ERROR: Third parameter should be a boolean')
        result = self.app.selectTool('data', 'R', True)
        self.assertEquals(result, 'ERROR: First parameter should be a data frame')
        result = self.app.selectTool(data, 10, True)
        self.assertEquals(result, 'ERROR: Second parameter should be a string')

    # tests for scoreTools()
    def test_scoreTools(self):
        file1 = self.app.readFile('data/Data Mining Tools.xlsx')
        file2 = self.app.readFile('data/Data Mining Tool Ratings.xlsx')
        data = self.app.joinData(file1, file2)
        tool_data = self.app.selectTool(data, 'RapidMiner', True)
        compare_data = self.app.selectTool(data, 'RapidMiner', False)
        result = self.app.scoreTools(tool_data, compare_data)
        self.assertEquals(len(result.columns), 16)
        result = self.app.scoreTools(tool_data, compare_data)
        self.assertEquals(len(result.columns) - len(tool_data.columns), 1)
        result = self.app.scoreTools(tool_data, 'compare_data')
        self.assertEquals(result, 'ERROR: First and second parameters should be data frames')
        result = self.app.scoreTools('tool_data', compare_data)
        self.assertEquals(result, 'ERROR: First and second parameters should be data frames')

if __name__ == '__main__':
    unittest.main()