from collections import defaultdict
import io
import json
import csv
import re
import http.client
import random
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ASCENDING
from bson import json_util
from flask import Flask, make_response, render_template, request, redirect, url_for, Response, flash, get_flashed_messages, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId

# Replace the placeholder with your Atlas connection string
uri = "mongodb://localhost:27017"

# Set the Stable API version when creating a new client
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["expense_tracker"]
collection = None 
basic_collection = None
username = ""
app = Flask(__name__)
app.secret_key = 'secret_key123'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])  # Convert ObjectId to string
        self.username = user_data['username']
        self.password = user_data['password']
        self.basic_collection_name = user_data["basic_collection_name"]
        self.financial_collection_name = user_data["financial_collection_name"]
        self.full_name = user_data["full_name"]
        self.email = user_data["email"]
        self.mobile_no = user_data["mobile_no"]

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        global collection
        collection = db[user_data["financial_collection_name"]]
        global basic_collection
        basic_collection = db[user_data["basic_collection_name"]]
        return User(user_data)
    
    return None

@app.route('/check-otp-page', methods=['GET', 'POST'])
def load_check_otp():
    if(session.get('otp')):
        return render_template('enter-otp.html')
    else:
        return redirect(url_for('send_req'))


    
@app.route('/reset-pw', methods=['GET', 'POST'])
def reset(): 
    if request.method == "POST":
        otp = request.form.get('otp')
        if(int(session['otp']) == int(otp)):
            password = request.form.get('password')
            c_password = request.form.get('c_password')
            if (password == c_password):
                collection = db["users"]
                filter = {"username": session['reset-pw-username']}
                update = {"$set": {"password" : generate_password_hash(password)}}
                collection.update_one(filter, update)
                session.pop('otp')
                session.pop('reset-pw-username')
                return render_template('login.html')
            else:
                flash('Credentials do not match!!')
        else:
            flash('Incorrect OTP, try again')
        return render_template('enter-otp.html')
    else:
        return redirect(url_for("send_req"))
    

@app.route('/send_reset_request', methods=['GET', 'POST'])
def send_req():
    return render_template('send-req.html')



@app.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if request.method == "POST":
        username = request.form.get('username')
        collection = db["users"]
        user_data = collection.find_one({"username":username})
        if(user_data):
            email = user_data["email"]
            otp = random.randint(111111,999999)
            session['otp'] = otp
            session['reset-pw-username'] = username
            email_request = ("http://localhost:8081/?email="+email+"&otp="+ str(otp))
            response = requests.get(email_request)
            flash(response.text)
            return redirect(url_for('load_check_otp'))


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        global username
        username = request.form.get('username')
        password = request.form.get('password')
        c_password = request.form.get('c_password')
        full_name = request.form.get('full-name')
        mobile_no = request.form.get('mobile-no')
        email = request.form.get('email')

        # #Check if both credenials match
        # if password == c_password:
        #     flash('Credentials do not match')
        #     return render_template('register.html')


        # Check if the username already exists
        if db.users.find_one({'username': username}):
            flash('This username is already taken')
            return render_template('register.html')

        # Create a new user document
        user_data = {
            'username': username,
            'password': generate_password_hash(password),  # Hash the password
            'basic_collection_name': "basic_structure_" + username,
            'financial_collection_name': "financial_records_" + username,
            'full_name': full_name,
            'email': email,
            'mobile_no': mobile_no,
        }
        db.users.insert_one(user_data)

        # Retrieve the newly created user's data
        user_data = db.users.find_one({'username': username})
        new_user = User(user_data)
        
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        global username
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = db.users.find_one({'username': username})

        if not user_data:
            flash("User does not exists")
            return render_template('login.html')

        if check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Wrong password")
            return render_template('login.html', err_msg="Wrong password", data1=username)
    return render_template('login.html')



@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = current_user.username
        password = request.form.get('password')
        full_name = request.form.get('full-name')
        mobile_no = request.form.get('mobile-no')
        email = request.form.get('email')

        if check_password_hash(current_user.password, password):
            update_query_result = db.users.update_one({"username": username}, {"$set": {
                "full_name": full_name,
                "email": email,
                "mobile_no": mobile_no
            }})

            print(update_query_result.modified_count)

            if update_query_result.modified_count > 0:
                flash("Details Updated")
                return redirect(url_for('index'))
            else:
                flash("Could not update details, update query failed")
                return redirect(url_for('index'))
        else:
            flash("Wrong password")
            return render_template("edit-profile.html", 
                           usrname=username, 
                           full_name=full_name, 
                           email=email, 
                           mobile_no=mobile_no)        

    return render_template("edit-profile.html", 
                           usrname=current_user.username, 
                           full_name=current_user.full_name, 
                           email=current_user.email, 
                           mobile_no=current_user.mobile_no)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def getINR(amt, cur):
    amt = int(amt)
    if amt == "USD":
        return amt * 82.73
    elif amt == "GBP": 
        return amt * 104.53
    elif amt == "EUR":
        return amt * 89.43
    return amt
            

@app.route('/insert', methods=['GET'])
@login_required
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

    if len(list(collection.find({"date": json_data["date"]}))) > 0:
        collection.replace_one({"date":json_data["date"]}, json_data)
    else:
        collection.insert_one(json_data)
        
    print(json_data)
    return "Data inserted"

@app.route("/edit/<month>", methods=["GET"])
@login_required
def edit_data(month):
    return render_template("edit-data.html", month_name=month)

@app.route("/get-overall-data", methods=["GET"])
@login_required
def overall_data():
    total_amt_inr = 0
    total_income = 0
    try:
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
    except:
        return Response(json.dumps({
            "total-income": 0,
            "total-expense": 0,
            "profit-ratio": 0
        }), content_type='application/json')

@app.route("/delete-account", methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "POST":
        collection.drop();
        basic_collection.drop()
        db.users.delete_one({"username": current_user.username})
        logout_user()
        flash("Your account has been deleted")
        return render_template("login.html")
    return render_template("delete-account.html")

@app.route('/view', methods=['GET'])
@login_required
def view_data():
    data = request.args.get('data')
    results = collection.find({"date": data})
    json_data = json.dumps(list(results), default=json_util.default)
    return Response(json_data, content_type='application/json')

@app.route("/view-month/<month>", methods=["GET"])
@login_required
def view_month(month):
    return render_template("view-month.html", month_name=month)

from flask import make_response

@app.route("/generate-csv/<month>", methods=["GET"])
@login_required
def generate_csv(month):
    results = collection.find({"date": month})

    # Create a stream to hold CSV data
    csv_stream = io.StringIO()

    # Initialize the CSV writer with the stream
    writer = csv.DictWriter(csv_stream, fieldnames=['category', 'name', 'amt', 'cur', 'loc', 'amt_inr'])

    # Write the CSV data to the stream

    for document in results:
        writer.writerow({
            'category': 'profit',
            'name': '',
            'amt': document['profit'],
            'cur': '',
            'loc': '',
            'amt_inr': ''
        })
        writer.writerow({
            'category': 'total_expenses',
            'name': '',
            'amt': document['total_expense'],
            'cur': '',
            'loc': '',
            'amt_inr': ''
        })
        writer.writerow({
            'category': 'month',
            'name': '',
            'amt': month,
            'cur': '',
            'loc': '',
            'amt_inr': ''
        })

        writer.writeheader()
        for category in document['categories']:
            for expense in category['expenses']:
                expense.pop('id', None)
                expense['category'] = category['name']
                writer.writerow(expense)
    csv_stream.seek(0)
    csv_data = csv_stream.getvalue()

    response = make_response(csv_data)
    response.headers["Content-Disposition"] = f"attachment; filename=output_{month}.csv"
    response.headers["Content-type"] = "text/csv"

    return response

@app.route("/get-years", methods=["GET"])
@login_required
def get_years():
    pipeline = [
        {"$group": {"_id": {"$substr": ["$date", 4, 5]}}}
    ]
    
    unique_years_cursor = collection.aggregate(pipeline)
    unique_years = [record["_id"] for record in unique_years_cursor]
    return unique_years

@app.route("/generate-annual-csv/<year>", methods=["GET"])
@login_required
def generate_annual_csv(year):
    year_pattern = re.compile(fr'_{year}$')
    results = collection.find({"date": {"$regex": year_pattern}})
    
    csv_stream = io.StringIO()

# Initialize the CSV writer with the stream
    writer = csv.writer(csv_stream)        
    category_totals = defaultdict(int)
    expense_totals = defaultdict(int)
    
    for idx, document in enumerate(results):
        # Write profit, total_expenses, and date rows
        writer.writerow(['profit', '', document['profit']])
        writer.writerow(['total_expenses', '', document['total_expense']])
        writer.writerow(['date', '', document['date']])
        
        # Write the header row
        writer.writerow(['category', 'name', 'amt', 'cur', 'loc', 'amt_inr'])
        
        for category in document['categories']:
            for expense in category['expenses']:
                writer.writerow([category['name'], expense['name'], expense['amt'], expense['cur'], expense['loc'], expense['amt_inr']])
                category_totals[category['name']] += int(expense['amt_inr'])
                expense_totals[expense['name']] += int(expense['amt_inr'])
            
        writer.writerow([])  # Insert an empty row after each month's data
        
    # Write the total amount spent per category
    writer.writerow(['Total Category Amounts'])
    for category_name, category_total in category_totals.items():
        writer.writerow([category_name, 'Total:', '', '', '', category_total])
        
    writer.writerow([])  # Insert an empty row after the category totals
    
    # Write the total amount spent per expense
    writer.writerow(['Total Expense Amounts'])
    for expense_name, expense_total in expense_totals.items():
        writer.writerow([expense_name, 'Total:', '', '', '', expense_total])
    
    csv_stream.seek(0)
    csv_data = csv_stream.getvalue()

    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=output_all.csv"
    response.headers["Content-type"] = "text/csv"

    return response


@app.route("/generate-csv-all", methods=["GET"])
@login_required
def generate_csv_all():
    all_results = collection.find()  # Retrieve all records
    
    csv_stream = io.StringIO()

# Initialize the CSV writer with the stream
    writer = csv.writer(csv_stream)        
    category_totals = defaultdict(int)
    expense_totals = defaultdict(int)
    
    for idx, document in enumerate(all_results):
        # Write profit, total_expenses, and date rows
        writer.writerow(['profit', '', document['profit']])
        writer.writerow(['total_expenses', '', document['total_expense']])
        writer.writerow(['date', '', document['date']])
        
        # Write the header row
        writer.writerow(['category', 'name', 'amt', 'cur', 'loc', 'amt_inr'])
        
        for category in document['categories']:
            for expense in category['expenses']:
                writer.writerow([category['name'], expense['name'], expense['amt'], expense['cur'], expense['loc'], expense['amt_inr']])
                category_totals[category['name']] += int(expense['amt_inr'])
                expense_totals[expense['name']] += int(expense['amt_inr'])
            
        writer.writerow([])  # Insert an empty row after each month's data
        
    # Write the total amount spent per category
    writer.writerow(['Total Category Amounts'])
    for category_name, category_total in category_totals.items():
        writer.writerow([category_name, 'Total:', '', '', '', category_total])
        
    writer.writerow([])  # Insert an empty row after the category totals
    
    # Write the total amount spent per expense
    writer.writerow(['Total Expense Amounts'])
    for expense_name, expense_total in expense_totals.items():
        writer.writerow([expense_name, 'Total:', '', '', '', expense_total])
    
    csv_stream.seek(0)
    csv_data = csv_stream.getvalue()

    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=output_all.csv"
    response.headers["Content-type"] = "text/csv"

    return response



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

@app.route("/get-months-list", methods=["GET"])
@login_required
def month_list():

    data = {}
    for document in collection.find():
        data[document["date"]] = document["profit"]

    print(data)

    return Response(json.dumps(data, default=json_util.default), content_type='application/json')

@app.route("/get-sorted-expenses-by-loc-all", methods=["GET"])
@login_required
def sorted_expenses_loc_all():
    all_expenses = []
    for document in collection.find():
        for category in document['categories']:
            all_expenses.extend(category['expenses'])
    
    sorted_expenses = sorted(all_expenses, key=lambda expense: expense['amt_inr'], reverse=True)

    expenses_by_location = {}
    for expense in sorted_expenses:
        location = expense['loc']
        if location not in expenses_by_location:
            expenses_by_location[location] = []
        expenses_by_location[location].append(expense)

    return Response(json.dumps(expenses_by_location, default=json_util.default), content_type='application/json')

@app.route("/get-sorted-expenses-by-loc/<month>", methods=["GET"])
@login_required
def sorted_expenses_loc(month):
    all_expenses = []
    for document in collection.find({"date": month}):
        for category in document['categories']:
            all_expenses.extend(category['expenses'])
    
    sorted_expenses = sorted(all_expenses, key=lambda expense: expense['amt_inr'], reverse=True)

    expenses_by_location = {}
    for expense in sorted_expenses:
        location = expense['loc']
        if location not in expenses_by_location:
            expenses_by_location[location] = []
        expenses_by_location[location].append(expense)

    return Response(json.dumps(expenses_by_location, default=json_util.default), content_type='application/json')

@app.route("/top-cats-overall", methods=["GET"])
@login_required
def top_cats():
    categories_expenses = defaultdict(float)

    # Iterate through documents in the collection
    for document in collection.find():
        for category in document['categories']:
            for expense in category['expenses']:
                categories_expenses[category['name']] += expense['amt_inr']

    # Create a dictionary to store all categories and their expenses
    data = {}

    # Populate the data dictionary with categories and expenses
    for category, expense in categories_expenses.items():
        data[category] = expense
        
    return Response(json.dumps(data, default=json_util.default), content_type='application/json')

@app.route("/top-cats/<month>", methods=["GET"])
@login_required
def top_cats_month(month):
    categories_expenses = defaultdict(float)

    # Iterate through documents in the collection
    for document in collection.find({"date": month}):
        for category in document['categories']:
            for expense in category['expenses']:
                categories_expenses[category['name']] += expense['amt_inr']

    # Create a dictionary to store all categories and their expenses
    data = {}

    # Populate the data dictionary with categories and expenses
    for category, expense in categories_expenses.items():
        data[category] = expense
        
    return Response(json.dumps(data, default=json_util.default), content_type='application/json')


@app.route('/index', methods=['GET'])
@login_required
def index():
    return render_template("index.html")

@app.route('/delete', methods=['GET'])
@login_required
def delete_data():
    data = request.args.get('data')
    pw = request.args.get("password")
    if check_password_hash(current_user.password, pw):
        collection.delete_one({"date": data})
        return "success"
    else:
        return "wrong_pw"
    
@app.route('/insert-data', methods=['GET'])
@login_required
def insert_frontend():
    return render_template("insert-data.html")


@app.route('/add-category', methods=['GET'])
@login_required
def add_category():
    data = request.args.get('name')
    find_result = collection.find({"name": data})
    if len(list(find_result)) < 1:
        data_dict = {"name": data, "expenses":[]}
        json_data = json.dumps(data_dict)
        basic_collection.insert_one(data_dict)
        return "success"
    return "fail"

@app.route('/add-expense/<category_name>', methods=['GET'])
@login_required
def add_expense(category_name):
    data = request.args.get('expense')
    category_document = basic_collection.find_one({"name": category_name})
        
    if category_document:
        expenses = category_document.get("expenses", [])
        
        if data not in expenses:
            expenses.append(data)
            
        basic_collection.update_one({"name": category_name}, {"$set": {"expenses": expenses}})
        
        updated_category = basic_collection.find_one({"name": category_name})
        updated_category["_id"] = 0
        return "success"
    return "fail"

@app.route('/remove-category', methods=['GET'])
@login_required
def remove_category():
    data = request.args.get('name')
    basic_collection.delete_one({"name": data})
    return "success"

@app.route('/remove-expense/<category_name>', methods=['GET'])
@login_required
def remove_expense(category_name):
    data = request.args.get('expense')
    category_document = basic_collection.find_one({"name": category_name})
        
    if category_document:
        expenses = category_document.get("expenses", [])
        
        if data in expenses:
            expenses.remove(data)
            
        basic_collection.update_one({"name": category_name}, {"$set": {"expenses": expenses}})
        
        updated_category = basic_collection.find_one({"name": category_name})
        updated_category["_id"] = 0
        return "success"
    return "fail"

@app.route('/get-base', methods=['GET'])
@login_required
def get_base():
    documents = basic_collection.find({})
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
