from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'secret_key123'

client = MongoClient('mongodb://localhost:27017/')
db = client['expense_tracker']

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])  # Convert ObjectId to string
        self.username = user_data['username']
        self.password = user_data['password']

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        c_password = request.form.get('c_password')

        #Check if both credenials match
        if password == c_password:
            return render_template('register.html', err_msg="Credentials don't match", data1=username)


        # Check if the username already exists
        if db.users.find_one({'username': username}):
            # flash('err_field_1')
            return render_template('register.html', err_msg="This username is not available!", data1=username)

        # Create a new user document
        user_data = {
            'username': username,
            'password': generate_password_hash(password),  # Hash the password
            # Add other user attributes as needed
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
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = db.users.find_one({'username': username})

        if not user_data:
            # flash("err_field_1")
            return render_template('login.html', err_msg='Username does not exist', data1=username)

        if check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            # flash("err_field_2")
            return render_template('login.html', err_msg="Wrong password", data1=username)
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
