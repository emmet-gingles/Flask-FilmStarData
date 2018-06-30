from __future__ import print_function  # In python 2.7
from flask import Flask, jsonify, request, render_template
from flask_pymongo import PyMongo, pymongo
import datetime

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'test'
app.config['MONGO_URI'] = 'mongodb://localhost/test'
mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def listData():
    # default table
    table = mongo.db.actors
    fields = ['last name', 'first name', 'date of birth']
    # sort data in ascending order
    sortBy = pymongo.ASCENDING
    query = {}
    # position in result set to start from
    offset = 0
    # limit of how many results per page
    limit = 10
    # search for a particular string
    stringSearch = False
    # parameters to be used when searching for a particular string
    fname = ''
    lname = ''
    # search by date
    dateSearch = False
    #  parameters to be used when searching for a date range
    startDate = ''
    endDate = ''


    # if type parameter is set then get it from request.args
    # NOTE: request.args accepts parmeters from both the form element and a HTTP request
    if 'type' in request.args:
        type = request.args['type']
        # depending on what type was input as, select the appropriate collection from the database
        if type == "actors":
            table = mongo.db.actors
        elif type == "actresses":
            table = mongo.db.actresses
        elif type == "directors":
            table = mongo.db.directors
            # if anything else was input return error page
        else:
            return page_not_found(404)

    # if order parameter is set then get it from request.args
    if 'order' in request.args:
        order = request.args['order']
        # depending on what order was input select the fields to order the results by
        if order == "date":
            fields = ['date of birth', 'last name', 'first name']
        elif order == "lastname":
            fields = ['last name', 'first name', 'date of birth']
        elif order == "firstname":
            fields = ['first name', 'last name', 'date of birth']
        else:
            return page_not_found(404)

    # if sort parameter is set then get it from request.args
    if 'sort' in request.args:
        sortBy = request.args['sort']
        # depending on the input, sort in ascending or descending order
        if sortBy.upper() == "ASC":
            sortBy = pymongo.ASCENDING
        elif sortBy.upper() == "DESC":
            sortBy = pymongo.DESCENDING
        else:
            return page_not_found(404)

    # if either firstname OR lastname are set then get them from request.args
    if ('firstname' in request.args) or ('lastname' in request.args):
        stringSearch = True
        # depending on which are set, set their respective variables
        if ('firstname' in request.args):
            fname = request.args['firstname']
        if ('lastname' in request.args):
            lname = request.args['lastname']

    # if both startyear AND endyear are set then get them from request.args and set their respective variables
    if ('startyear' in request.args) and ('endyear' in request.args):
        startYear = request.args['startyear']
        endYear = request.args['endyear']
        dateSearch = True
        # try to cast them to integers, if not return error page
        try:
            startYear = int(startYear)
        except (ValueError, TypeError):
            return page_not_found(404)
        try:
            endYear = int(endYear)
        except (ValueError, TypeError):
            return page_not_found(404)
        # input parameters should fall within the range
        if startYear < 1890 or startYear > 2000:
            return page_not_found(404)
        if endYear < 1890 or endYear > 2000:
            return page_not_found(404)
        # set startdate to January 1st for that year
        startDate = datetime.datetime.strptime('0101'+str(startYear), "%d%m%Y");
        # set enddate to December 31st for that year
        endDate = datetime.datetime.strptime('3112'+str(endYear), "%d%m%Y");

    # if status parameter is set then get it from request.args
    if 'status' in request.args:
        status = request.args['status']
        # if status is equal to living
        if status == 'living':
            query = structureQuery(status, stringSearch, fname, lname, dateSearch, startDate, endDate )
        elif status == 'deceased':
            query = structureQuery(status, stringSearch, fname, lname, dateSearch, startDate, endDate)
        elif status == 'all':
            query = structureQuery(status, stringSearch, fname, lname, dateSearch, startDate, endDate)
        # else return error page
            print(query)
        else:
            return page_not_found(404);
    else:
        # structureQuery(status, stringSearch, fname, lname, dateSearch, startDate, endDate)
        query = structureQuery("none", stringSearch, fname, lname, dateSearch, startDate, endDate)

    # if offset parameter is set then get it from request.args
    if 'offset' in request.args:
        offset = request.args['offset']
        # try to cast to an integer, return error page if not
        try:
            offset = int(offset)
        except (ValueError, TypeError):
            return page_not_found(404)

    results = []
    # query the table and sort the results according to the parameters and loop through results set
    for data in table.find(query).sort([(fields[0], sortBy,), (fields[1], sortBy), (fields[2], sortBy)]):
        # if deceased include the date of their death and append columns to list
        if 'date of death' in data:
            results.append( {'name': data['first name'] + " " + data['last name'], "date of birth": data['date of birth'], "date of death": data['date of death'] })
        # else they are alive and append columns to list
        else:
            results.append({'name' : data['first name'] + " " + data['last name'], "date of birth" : data['date of birth'] })
    # total number of results
    totalResults = len(results)
    # set results set to start at offset and stop at offset + limit
    results = results[offset:offset+limit]
    # if AJAX request then convert variables to JSON object
    if request.is_xhr:
        return jsonify({'data': results, 'total': totalResults, 'offset': offset })
    # else use render template to show page and pass variables as parameters
    else:
        return render_template("showData.html", data=results, total=totalResults, offset=offset)

# function to return error page if input parameter is wrong
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# function that accepts three parameters - day, month and year and converts them into a date format
def formatDate(day, month, year):
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    d = str(int(day))
    m = months[int(month)-1]
    y = year
    dateformat = m + " " + d + ", " + y
    return dateformat

# function that uses its parameters to determine the structure of the database query
def structureQuery(status, stringSearch, fname, lname, dateSearch, startDate, endDate):
    # default parameter values
    query = {}
    isAlive = True

    # depending on the status change the boolean variable
    if status == "deceased":
        isAlive = False
    elif status == "living":
        isAlive = True

    # id true then one or both string parameters are set
    if(stringSearch):
        # if both firstname and lastname are set
        if fname != '' and lname != '':
            # create regular expressions for anything that matches the start
            s1 = '^' + fname
            s2 = '^' + lname
            # if status is either 'living' or 'deceased'
            if status == "living" or status == "deceased":
                # if true then both date parameters are set so include them in query
                if(dateSearch):
                    query = {'first name': {'$regex': s1, '$options': 'i'},
                            'last name': {'$regex': s2, '$options': 'i'},
                            "date of birth": {'$gte': startDate, '$lte': endDate},
                            'isAlive': {"$eq": isAlive}}
                # else neither parameter is set so construct query without dates
                else:
                    query = {'first name': {'$regex': s1, '$options': 'i'},
                                     'last name': {'$regex': s2, '$options': 'i'},
                                     'isAlive': {"$eq": isAlive}}
            # else status is equal to 'all'
            else:
                if (dateSearch):
                    query = {'first name': {'$regex': s1, '$options': 'i'},
                             'last name': {'$regex': s2, '$options': 'i'},
                             "date of birth": {'$gte': startDate, '$lte': endDate}}
                else:
                    query = {'first name': {'$regex': s1, '$options': 'i'},
                            'last name': {'$regex': s2, '$options': 'i'}}
        # else if only firstname is set
        elif fname != "":
            s1 = '^' + fname
            if status == "living" or status == "deceased":
                if(dateSearch):
                    query = {'first name': {'$regex': s1, '$options': 'i'},
                                     "date of birth": {'$gte': startDate, '$lte': endDate},
                                     'isAlive': {"$eq": isAlive}}
                else:
                    query = {'first name': {'$regex': s1, '$options': 'i'},
                                     'isAlive': {"$eq": isAlive}}
            else:
                if (dateSearch):
                    query = {'first name': {'$regex': s1, '$options': 'i'},
                             "date of birth": {'$gte': startDate, '$lte': endDate}}
                else:
                    query = {'first name': {'$regex': s1, '$options': 'i'}}
        # else if only lastname is set
        elif lname != '':
            s2 = '^' + lname
            if status == "living" or status == "deceased":
                if(dateSearch):
                    query = {'last name': {'$regex': s2, '$options': 'i'},
                                     "date of birth": {'$gte': startDate, '$lte': endDate},
                                     'isAlive': {"$eq": isAlive}}
                else:
                    query = {'last name': {'$regex': s2, '$options': 'i'},
                                     'isAlive': {"$eq": isAlive}}
            else:
                if (dateSearch):
                    query = {'last name': {'$regex': s2, '$options': 'i'},
                             "date of birth": {'$gte': startDate, '$lte': endDate}}
                else:
                    query = {'last name': {'$regex': s2, '$options': 'i'}}
        # else if neither firstname or lastname is set then construct query without string parameters
        else:
            if(status != "none"):
                # if variable is True then search by date range
                if (dateSearch):
                    query = {"date of birth": {'$gte': startDate, '$lte': endDate},
                         'isAlive': {"$eq": isAlive}}
                # otherwise it is False so dont use a date range
                else:
                    query = {'isAlive': {"$eq": isAlive}}
            else:
                if(dateSearch):
                    query = {"date of birth": {'$gte': startDate, '$lt': endDate}}
    # else if neither string parameters are set
    else:
        # if status is either 'living' or 'deceased'
        if status == "living" or status == "deceased":
            # if variable is True then search by date range
            if (dateSearch):
                query = {"date of birth": {'$gte': startDate, '$lte': endDate},
                      'isAlive': {"$eq": isAlive}}
            # otherwise it is False so dont use a date range
            else:
                query = {'isAlive': {"$eq": isAlive}}
        # else status is 'all'
        else:
            # if variable is True then construct query to just search by date range
            if (dateSearch):
                query = {"date of birth": {'$gte': startDate, '$lte': endDate}}
            # else make query empty so it will return everything from table
            else:
                query = {}
        print(query)
    return query


# allows function to be called by jinja
app.jinja_env.globals.update(formatDate=formatDate)


# String search
# db.actors.find({"last name" : { $regex : /^al/i }}).sort({"last name": 1})
#Note: i stands case-insensitive


if __name__ == '__main__':
    app.run(debug=True)