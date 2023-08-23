import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ASCENDING
from flask import Flask, request, Response, render_template, jsonify
from bson import json_util

# Replace the placeholder with your Atlas connection string
uri = "mongodb://localhost:27017"

# Set the Stable API version when creating a new client
client = MongoClient(uri, server_api=ServerApi('1'))

expense_db = client["expense_tracker"]
collection = expense_db["expense_income_details"]

# def get_expense(json_data):

# def get_income():
# def calculate_profit():
        

app = Flask(__name__)

@app.route('/manage', methods=['GET'])
def manage():
    return render_template("manage.html")

def getINR(amt, cur):
    amt = int(amt)
    match cur: 
        case "USD":
            return amt * 82.73
        case "GBP": 
            return amt * 104.53
        case "EUR":
            return amt * 89.43
    return amt
            

@app.route('/insert', methods=['GET'])
def insert_data():
    data = request.args.get('data')
    json_data = json.loads(data)
    total_expense = 0
    for cat in json_data["categories"]:
        expenses = cat["expenses"]
        for expense in expenses:
            expense["amt_inr"] = round(getINR(expense["amt"], expense["cur"]))
            print(expense["name"], expense["amt_inr"])
            total_expense += expense["amt_inr"]
            
    profit_ratio = 100 - round(((total_expense * 100)/ int(json_data["income"])), 2)
    json_data["total_expense"] = total_expense
    json_data["profit"] = profit_ratio
    collection.insert_one(json_data)
    print(json_data)
    return "Data inserted"

@app.route("/get-overall-data", methods=["GET"])
def overall_data():
    total_amt_inr = 0
    total_income = 0
    for document in collection.find():
        total_income += float(document['income'])
        for category in document['categories']:
            for expense in category['expenses']:
                total_amt_inr += expense['amt_inr']

    profit_ratio = 100 - round(((total_amt_inr * 100)/ int(total_income)), 2)

    data = {
        "total-income": total_income,
        "total-expense": total_amt_inr,
        "profit-ratio": profit_ratio
    }

    return Response(json.dumps(data), content_type='application/json')



@app.route('/view', methods=['GET'])
def view_data():
    data = request.args.get('data')
    results = collection.find({"date": data})
    json_data = json.dumps(list(results), default=json_util.default)
    return Response(json_data, content_type='application/json')

@app.route("/get-sorted-expenses/<month>", methods=["GET"])
def sorted_expenses(month):
    all_expenses = []
    for document in collection.find({"date": month}):
        for category in document['categories']:
            all_expenses.extend(category['expenses'])
    sorted_expenses = sorted(all_expenses, key=lambda expense: expense['amt_inr'])

    sorted_expenses.reverse()

    for expense in sorted_expenses:
        print(expense)

    return sorted_expenses;

@app.route("/get-sorted-expenses-by-loc/<month>", methods=["GET"])
def sorted_expenses_loc(month):
    all_expenses = []
    for document in collection.find({"date": month}):
        for category in document['categories']:
            all_expenses.extend(category['expenses'])
    sorted_expenses = sorted(all_expenses, key=lambda expense: expense['loc'])

    sorted_expenses.reverse()

    for expense in sorted_expenses:
        print(expense)

    return sorted_expenses;

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