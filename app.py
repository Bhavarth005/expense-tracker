import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, request, Response, render_template
from bson import json_util

# Replace the placeholder with your Atlas connection string
uri = "mongodb://localhost:27017"

# Set the Stable API version when creating a new client
client = MongoClient(uri, server_api=ServerApi('1'))

expense_db = client["expense_tracker"]
collection = expense_db["expense_income_details"]

app = Flask(__name__)

@app.route('/insert', methods=['GET'])
def insert_data():
    data = request.args.get('data')
    json_data = json.loads(data)
    
    collection.insert_one(json_data)
    return "Data inserted"

@app.route('/view', methods=['GET'])
def view_data():
    
    data = request.args.get('data')
    results = collection.find({"date": data})
    json_data = json.dumps(list(results), default=json_util.default)
    return Response(json_data, content_type='application/json')

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/update', methods=['GET'])
def update_data():
    data = request.args.get('data')
    json_data = json.loads(data)
    collection.update_one({"date": json_data["date"]}, {"$set" : json_data})
    return "Data Updated"

@app.route('/delete', methods=['GET'])
def delete_data():
    data = request.args.get('data')
    collection.delete_one({"date": data})
    return "Data Deleted"
    
# @app.route('/add', methods=['GET'])


if __name__ == '__main__':
    app.run(debug=True)