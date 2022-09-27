from urllib import response
from flask import Flask, render_template, request, send_file, redirect, url_for, session
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import requests
import subprocess
import re

from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.secret_key = '3R\xfc\xddVY0\x87jW/\x9b\x9fVy\x9e\x1e/\xc1\xaf\x9a\x14\xf6B'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Flask2022!'
app.config['MYSQL_DB'] = 'users'

mysql = MySQL(app)


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/pythonlogin/logout')
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

# this will be the registration page, we need to use both GET and POST requests


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute(
                'INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/stocks')
def stocks():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the stock page
        return render_template('stocks.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/blog')
def blog():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the stock page
        return render_template('blog.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



@app.route('/generate', methods=["GET", "POST"])
def generate():
    if request.method == "POST":

        first_name = request.form.get("fname")
        last_name = request.form.get("lname")
        tickerOption = request.form.get("ticker")
        dateOption = request.form.get("time-dropdown")

        #end_date = date.today().strftime("%Y-%m-%d")
        newest_available_date = "2018-03-27"

        end_date = datetime.strptime(newest_available_date, "%Y-%m-%d")
        #end_date = end_date.strftime("%Y-%m-%d")

        if dateOption == "3":
            start_date = end_date - relativedelta(months=+3)
        elif dateOption == "6":
            start_date = end_date - relativedelta(months=+6)
        else:
            start_date = end_date - relativedelta(months=+12)

        start_date = start_date.strftime("%Y-%m-%d")
        url_api_call = "https://data.nasdaq.com/api/v3/datasets/WIKI/"+tickerOption+".json?start_date=" + \
            start_date+"&end_date="+newest_available_date + \
            "&order=asc&api_key=LhpSY93Li7WXbet5_yi6"
        url_csv_file = "https://data.nasdaq.com/api/v3/datasets/WIKI/"+tickerOption+".csv?start_date=" + \
            start_date+"&end_date="+newest_available_date + \
            "&order=asc&api_key=LhpSY93Li7WXbet5_yi6"

        #response = requests.get("https://data.nasdaq.com/api/v3/datasets/WIKI/AAPL.json?start_date=1985-05-01&end_date=1997-07-01&order=asc&api_key=XoQQzN7nCkktZBwqse24")
        response = requests.get(url_api_call)
        jsonResponse = response.json()

        # print(url_api_call)
        tickOpt = subprocess.check_output(["echo", tickerOption])
        print(tickOpt)

        # print(response.json())
        if request.form.get('generate1') == 'json':
            message = "Your JSON data of Ticker:"+tickerOption + \
                " for "+dateOption+" Months is below"
            return render_template("stocks.html", username=session['username'], name=first_name, msg=message, note=jsonResponse)

        if request.form.get('generate2') == 'csv':
            req = requests.get(url_csv_file)
            url_content = req.content
            csvFileName = tickerOption+"-"+dateOption+'months.csv'
            csv_file = open(csvFileName, 'wb')
            csv_file.write(url_content)
            csv_file.close()
            #message = "File Download has been completed for CSV file of Ticker:"+tickerOption+ " for "+dateOption+" Months"
            #csvResponse = "Thank you !"
            # render_template("index.html",name=first_name,msg=message,note=csvResponse)
            return send_file(csvFileName, as_attachment=True)
