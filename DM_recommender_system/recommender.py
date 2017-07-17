from flask import Flask, render_template, request
from pandas import pandas as pd
import os

# instance of Flask
app = Flask(__name__)

# decorator for the index page
@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

# decorator for the attribute page
@app.route('/attribute/', methods=['GET','POST'])
def attribute():
    # if the request is a GET then just return the page
    if request.method == 'GET':
        return render_template('attribute_selector.html')
    # else it is a POST request sent from a form
    else:
        # get the data from AJAX and call splitString() to convert it into a tuple
        string = request.values.get('data')
        out = splitString(string)
        # create an attributes and values list from tuple
        attr = list(out[0])
        val = list(out[1])
        # get the results limit from the end of the values list and cast to an integer
        res_limit = val[-1]
        res_limit = int(res_limit)
        # remove the last element from both list as they are not part of the query
        attr.pop()
        val.pop()
        # call readFile() to find 'Data Mining Tools' Excel file
        file1 = readFile('data/Data Mining Tools.xlsx')
        # call readFile() to find the 'Data Mining Tools Ratings' Excel file
        file2 = readFile('data/Data Mining Tool Ratings.xlsx')
        # check that both files are data frames, before proceeding
        if isinstance(file1, pd.DataFrame) & isinstance(file2, pd.DataFrame):
            # call joinData() to join the data frames
            joinedData = joinData(file1, file2)
            # check that joinedData is a data frame, before proceeding
            if isinstance(joinedData, pd.DataFrame):
                # call searchData() to search the data using the attributes and values lists
                data = searchData(joinedData, attr, val)
                # check that data is a data frame, before proceeding
                if isinstance(data, pd.DataFrame):
                    # check that there is data in the data frame
                    if len(data) > 0:
                        # use results limit to limit the number of results returned
                        data = data.head(res_limit)
                        # remove indexes from the data frame and return it to user as a HTML table
                        return data.to_html(index=False)
                    # else there is no data in the data frame, let the user know
                    else:
                        return 'No records were found that match those parameters. Try searching again'
                else:
                    return 'There was an error retrieving the data'
            else:
                return 'There was an error retrieving the data'
        else:
            return 'There was an error retrieving the data'

# decorator for the tool page
@app.route('/tool/', methods=['GET','POST'])
def tool():
    # if the request is a GET just return the page
    if request.method == 'GET':
        return render_template('tool_selector.html')
    # else it is a post request sent from a form
    else:
        # get the tool data from AJAX
        sel_tool = request.values.get('tool')
        # if the data is 'SQL' then change it to 'SQL Server'
        if sel_tool == 'SQL':
            sel_tool = 'SQL Server'
        # get the results limit from AJAX
        res_limit = request.values.get('res_limit')
        res_limit = int(res_limit)
        # call readFile() to find the 'Data Mining Tools' Excel file
        file1 = readFile('data/Data Mining Tools.xlsx')
        file2 = readFile('data/Data Mining Tool Ratings.xlsx')
        if isinstance(file1, pd.DataFrame) & isinstance(file2, pd.DataFrame):
            # call joinData() to join the data frames
            joinedData = joinData(file1, file2)
            # check that joinedData is a data frame, before proceeding
            if isinstance(joinedData, pd.DataFrame):
                # call selectTool() twice using respective True and False values
                tool_data = selectTool(joinedData, sel_tool, True)
                compare_data = selectTool(joinedData, sel_tool, False)
                # check that both variables are data frames, before proceeding
                if isinstance(tool_data, pd.DataFrame) & isinstance(compare_data, pd.DataFrame):
                    # call scoreTools() using the return values of selectTools()
                    res = scoreTools(tool_data, compare_data)
                    # check that value returned is a data frame, before proceeding
                    if isinstance(res, pd.DataFrame):
                        # use results limit to limit the number of results returned
                        res = res.head(res_limit)
                        # remove the indexes from the data frame and return it to the user as a HTML table
                        return res.to_html(index=False)
                    else:
                        return 'There was an error retrieving the data'
                else:
                    return 'There was an error retrieving the data'
            else:
                return 'There was an error retrieving the data'
        else:
            return 'There was an error retrieving the data'

# function that splits a string input into a tuple of attributes and values
def splitString(str):
    # check that the string contains an '=', return an error if not
    if '=' not in str:
        return "ERROR: String must contain '='"
    else:
         # split string into list using '&'. String is only split if it contains more than one attribute
         lst = str.split('&')
         # setup lists for attributes and values
         attributes = []
         values = []
         # loop through list
         for l in lst:
            # split the current string into list using '='
            newlst = l.split('=')
            # append the first and second elements to attributes and values respectively
            attributes.append(newlst[0])
            values.append(newlst[1])
            # return a tuple consisting of both list
    return attributes, values

# function to read a file stored in a directory and return a data frame
def readFile(filepath):
    # check that the file name is a string, return an error if not
    if not isinstance(filepath, basestring):
         return "ERROR: First Parameter should be a string"
    # check filepath is valid
    if os.path.isfile(filepath):
        # use Pandas to read in the file and return a data frame
        data = pd.read_excel(filepath)
        return data
    else:
        return "ERROR: File not found"


# function to join two data frames
def joinData(data1, data2):
    # check that both parameters are data frames, return an error if not
    if not isinstance(data1, pd.DataFrame) & isinstance(data2, pd.DataFrame):
        return "ERROR: First and second parameters should be data frames"
    else:
        # assign both data frames to variables
        data_tools = data1
        ratings = data2
        # group the ratings by the column 'Tool_ID' and get the average for each, assign this to a new variable avg
        avg = ratings.groupby(['Tool_ID']).mean().reset_index()
        # round the ratings to one decimal place
        avg = avg.round({'Rating': 1})
        # rename the 'Rating' column to average rating
        avg = avg.rename(columns={'Rating': 'Average Rating'})
        # use Pandas to join data_tools and avg using 'Tool_ID'
        joinData = pd.merge(data_tools, avg, how='inner', on='Tool_ID')
        # drop the columns 'Tool_ID' and 'Rating_ID'
        joinData = joinData.drop('Tool_ID', axis=1)
        joinData = joinData.drop('Rating_ID', axis=1)
        return joinData

# function to search a data frame using attributes and values and returns the resulting data
def searchData(dta,l1,l2):
    # check that the first parameter is a data frame, return an error if not
    if not isinstance(dta, pd.DataFrame):
        return "ERROR: First parameter should be a data frame"
    # check that the second and third parameters are lists, return an error if not
    elif not isinstance(l1, list) & isinstance(l2, list):
        return "ERROR: First and second parameters should be lists"
    # check that the data frame has at least one row of data, return an error if not
    elif len(dta) == 0:
        return "ERROR: Data frame cannot contain no data"
    # check that both lists contain values, return an error if not
    elif len(l1) == 0 | len(l2) == 0:
        return "ERROR: List cannot contain no values"
    # check that both lists are the same size, return an error if not
    elif len(l1) != len(l2):
            return "ERROR: Lists must be the same size"
    else:
        data = ''
        # for each attribute
        for l in range(len(l1)):
            # if data already has some data then it is not the first time through the loop, run query for the current attribute
            if len(data) > 0:
                data = data[(data[l1[l]] == l2[l])]
            # else it is the first time through loop, run query for the current attribute
            else:
                data = dta[(dta[l1[l]] == l2[l])]
        # NOTE: the following statements do not require if statements but I put them in to guard against errors
        # two columns are renamed to remove underscores
        if 'Open_source' in data.columns:
            data = data.rename(columns={'Open_source': 'Open source'})
        if 'Text_Mining' in data.columns:
            data = data.rename(columns={'Text_Mining': 'Text Mining'})
        # the data is sorted by 'Average Rating' in descending order
        if 'Average Rating' in data.columns:
            data = data.sort_values(by=['Average Rating'], ascending=[0])
        return data

# function to search a data frame for a tool
def selectTool(data, tool_name, condition):
    # check tha the first parameter is a data frame, return an error if not
    if not isinstance(data, pd.DataFrame):
        return "ERROR: First parameter should be a data frame"
    # check that the second parameter is a string, return an error if not
    elif not isinstance(tool_name, basestring):
        return "ERROR: Second parameter should be a string"
    # check that the third parameter is a Boolean, return an error if not
    elif not isinstance(condition, bool):
        return "ERROR: Third parameter should be a boolean"
    else:
        # if the condition is True then search data frame for any rows where the 'Tool' column equals the tool_name,
        # remove index and return data frame
        if condition == True:
            data = data[(data['Tool'] == tool_name)]
            return data.reset_index(drop=True)
        # else if the condition is False then search the data frame for any rows where the 'Tool' column is not equal to
        #  the tool_name, remove index and return the data frame
        elif condition == False:
            data = data[(data['Tool'] != tool_name)]
            return data.reset_index(drop=True)

# function to compare one data frame to another and score each tool based on its similarity
def scoreTools(tool_data, compare_data):
    # check that both parameters are data frames, return an error if not
    if not isinstance(tool_data, pd.DataFrame) & isinstance(compare_data, pd.DataFrame):
        return "ERROR: First and second parameters should be data frames"
    else:
        # list of attributes that will be used to compare the data frames
        lstAttributes = ['Free','Open_source','Community','GUI','Scalable','Graphs','ETL','Text_Mining','Predictive','Algorithms']
        # add a new column to data frame for score
        compare_data['Score'] = ""
        # loop through each of the tools in the second data frame
        for i in range(0,len(compare_data)):
            # reset score for each loop
            score = 0
            # loop through the list of attributes
            for j in range(0,len(lstAttributes)):
                col = lstAttributes[j]
                # if attribute value is the same in both data frames
                if (tool_data[col][0] == compare_data[col][i]):
                    # increment score
                    score = score + 1
                    # find the row in the compare_data that has that tool and set its score
                    compare_data.iloc[i, compare_data.columns.get_loc('Score')] = score
        # NOTE: the following statements do not require if statements but I put them in to guard against errors
        # two columns are renamed to removed underscores
        if 'Open_source' in compare_data.columns:
            compare_data = compare_data.rename(columns={'Open_source': 'Open source'})
        if 'Text_Mining' in compare_data.columns:
            compare_data = compare_data.rename(columns={'Text_Mining': 'Text Mining'})
        # the data is sorted by 'Average Rating' in descending order
        if 'Average Rating' in compare_data.columns:
            compare_data = compare_data.sort_values(by=['Score', 'Average Rating'], ascending=[0, 0])
        return compare_data

if __name__ == "__main__":
    app.run(debug='True')