from time import time
from flask import Flask, request
from pymongo import MongoClient
import json
from bson import json_util, ObjectId
from markupsafe import escape
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt_identity, JWTManager)
app = Flask(__name__)
app.secret_key = '123456'
app.config['SESSION_TYPE'] = 'auth0'
jwt = JWTManager(app)

client = MongoClient("mongodb+srv://Avish:ezwGcvJUm7hK1IWK@cluster0.u6fdh.mongodb.net/Products?retryWrites=true&w=majority")
myDatabase = client['nurturelabs']

@app.route("/")
def hello_world():
    return "<p>Hello LLC</p>"

@app.route("/admin/advisor", methods=['GET', 'POST'])
def addAdvisor():
    if request.method == "POST":
        if(request.json['name'] and request.json['image_url']):
            query = myDatabase.advisor.insert_one(request.json)
            if(query != None):
                return {
                    'message': 'Advisor Added',
                    'status': 200,
                }
        else:
            return {
                'message':'BAD REQUEST',
                'status': 400
            }

@app.route('/user/register', methods=['GET', 'POST'])
def registerUser():
    if request.method == "POST":
        if(request.json['name'] and request.json['email'] and request.json['password']):
            accessToken = create_access_token(identity=request.json['password'])
            emailExists = myDatabase.userData.find_one({'email': request.json['email']})
            if (emailExists == None):
                try:
                    query = myDatabase.userData.insert_one(request.json)
                    if(query):
                        return {
                            'jwt Token': accessToken,
                            'user_id': str(query.inserted_id),
                            'status': 200
                        }
                except Exception as err:
                    return {
                            'message': 'Server Error',
                            'status': 400
                        }
            else:
                return {
                    'message': 'User Exists'
                }
    else:
        return {
                    'message': 'BAD REQUEST',
                    'status': 400
                }
    
@app.route('/user/login', methods=['GET', 'POST'])
def loginUser():
    if request.method == "POST":
        if(request.json['email'] and request.json['password']):
            query = myDatabase.userData.find_one(request.json)
            accessToken = create_access_token(identity=request.json['password'])
            if(query != None):
                return {
                    'jwt Token': accessToken,
                    'user_id': str(query['_id'])
                }
            else:
                return {
                    'message': 'Authentication Error',
                    'status': 401
                }
        else:
            return {
                'message': 'BAD REQUEST',
                'status': 400
            }

@app.route('/user/<string:userId>/advisor/<string:advisorId>/', methods=['GET', 'POST'])
def bookCalls(userId, advisorId):
    if request.method == "POST":
        userExists = myDatabase.userData.find({'_id': ObjectId(escape(userId))})
        advisorExists = myDatabase.advisor.find({'_id': ObjectId(escape(advisorId))})
        if(userExists != None and advisorExists != None):
            requestData = {
                'user_id': escape(userId),
                'advisor_id': escape(advisorId),
                'time': request.json['time']
            }
            query = myDatabase.bookings.insert_one(requestData)
            if(query):
                return {
                    'message':'booking done',
                    'status': 200
                }
        else:
            return {
                'message': 'BAD REQUEST',
                'status': 400
            }



@app.route('/user/<string:userid>/advisor', methods=['GET', 'POST'])
def getAdvisors(userid):
    if request.method == "GET":
        advisorData = []
        userExists = myDatabase.userData.find({'_id': ObjectId(escape(userid))})
        if(userExists != None):
            query = myDatabase.advisor.find()
            for data in query:
                advisorData.append(json.loads(json_util.dumps(data)))
            if(query):
                return {
                    'data': advisorData
                }
            else:
                return {
                    'message': 'BAD REQUEST',
                    'status': 400
                }

@app.route('/user/<string:userId>/advisor/bookings', methods=['GET', 'POST'])
def getCalls(userId):
    if request.method == "GET":
        bookings = []
        userExists = myDatabase.userData.find({'_id': ObjectId(escape(userId))})
        if(userExists!=None):
            getbookings = myDatabase.bookings.find()
            for booking in getbookings:
                tempArray = []
                getAdvisor = myDatabase.advisor.find_one({'_id': ObjectId(booking['advisor_id'])})
                tempArray.append(json.loads(json_util.dumps(getAdvisor)))
                tempArray.append(booking)
                bookings.append(tempArray)
            return {
                'data': json.loads(json_util.dumps(bookings))
            }


