import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, request, Response, render_template, jsonify
from bson import json_util

# Replace the placeholder with your Atlas connection string
uri = "mongodb://localhost:27017"

# Set the Stable API version when creating a new client
client = MongoClient(uri, server_api=ServerApi('1'))

expense_db = client["expense_tracker"]
collection = expense_db["expense_income_details"]

app = Flask(__name__)

@app.route('/manage', methods=['GET'])
def manage():
    return render_template("manage.html")


@app.route('/insert', methods=['GET'])
def insert_data():
    data = request.args.get('data')
    json_data = json.loads(data)
    # json_data["expenses"] = 
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
    return "success"

@app.route('/delete', methods=['GET'])
def delete_data():
    data = request.args.get('data')
    collection.delete_one({"date": data})
    return "success"
    
@app.route('/insert-data', methods=['GET'])
def insert_frontend():
    return render_template("insert-data.html")


@app.route('/add-category', methods=['GET'])
def add_category():
    collection = expense_db["basic_structure"]
    data = request.args.get('name')
    find_result = collection.find({"name": data})
    if len(list(find_result)) < 1:
        data_dict = {"name": data, "expenses":[]}
        json_data = json.dumps(data_dict)
        collection.insert_one(data_dict)
        return "success"
    return "fail"

@app.route('/add-expense/<category_name>', methods=['GET'])
def add_expense(category_name):
    collection = expense_db["basic_structure"]
    data = request.args.get('expense')
    category_document = collection.find_one({"name": category_name})
        
    if category_document:
        expenses = category_document.get("expenses", [])
        
        if data not in expenses:
            expenses.append(data)
            
        collection.update_one({"name": category_name}, {"$set": {"expenses": expenses}})
        
        updated_category = collection.find_one({"name": category_name})
        updated_category["_id"] = 0
        return "success"
    return "fail"

@app.route('/remove-category', methods=['GET'])
def remove_category():
    collection = expense_db["basic_structure"]
    data = request.args.get('name')
    collection.delete_one({"name": data})
    return "success"

@app.route('/remove-expense/<category_name>', methods=['GET'])
def remove_expense(category_name):
    collection = expense_db["basic_structure"]
    data = request.args.get('expense')
    category_document = collection.find_one({"name": category_name})
        
    if category_document:
        expenses = category_document.get("expenses", [])
        
        if data in expenses:
            expenses.remove(data)
            
        collection.update_one({"name": category_name}, {"$set": {"expenses": expenses}})
        
        updated_category = collection.find_one({"name": category_name})
        updated_category["_id"] = 0
        return "success"
    return "fail"

@app.route('/get-base', methods=['GET'])
def get_base():
    collection = expense_db["basic_structure"]
    documents = collection.find({})
    document_list = [doc for doc in documents]
    # json_data = json.loads(list(documents), default=json_util.default)
    base_data = {
        "categories" : {}
    }
    for entry in document_list:
        category_name = entry["name"]
        expenses = entry["expenses"]
    
        simplified_expenses = [{"name": expense} for expense in expenses]
    
        base_data["categories"][category_name] = simplified_expenses
    json_data = json.dumps(base_data)
    return Response(json_data, content_type='application/json')

if __name__ == '__main__':
    app.run(debug=True)