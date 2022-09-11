from tkinter import E
from urllib import response
from flask import Flask, render_template, request
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import requests

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

app.run(host='127.0.0.1', port=8080)

global url_csv_file


@app.route('/generate', methods =["GET", "POST"])
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
            url_api_call = "https://data.nasdaq.com/api/v3/datasets/WIKI/"+tickerOption+".json?start_date="+start_date+"&end_date="+newest_available_date+"&order=asc&api_key=XoQQzN7nCkktZBwqse24"
            url_csv_file = "https://data.nasdaq.com/api/v3/datasets/WIKI/"+tickerOption+".csv?start_date="+start_date+"&end_date="+newest_available_date+"&order=asc&api_key=XoQQzN7nCkktZBwqse24"

            #response = requests.get("https://data.nasdaq.com/api/v3/datasets/WIKI/AAPL.json?start_date=1985-05-01&end_date=1997-07-01&order=asc&api_key=XoQQzN7nCkktZBwqse24")
            response = requests.get(url_api_call)
            jsonResponse = response.json()
            print(tickerOption)
            print(url_api_call)
            #print(response.json())
            if request.form.get('generate1') == 'json':
                message = "Your JSON data of Ticker:"+tickerOption+ " for "+dateOption+" Months is below"
                return render_template("index.html",name=first_name,msg=message,note=jsonResponse)

            if request.form.get('generate2') == 'csv':
                req = requests.get(url_csv_file)
                url_content = req.content
                csv_file = open(tickerOption +'downloaded.csv', 'wb')
                csv_file.write(url_content)
                csv_file.close()
                message = "File Download has been completed for CSV file of Ticker:"+tickerOption+ " for "+dateOption+" Months"
                csvResponse = "Thank you !"
                return render_template("index.html",name=first_name,msg=message,note=csvResponse)


    # if request.method == "GET":
    #     #csv_url = "https://data.nasdaq.com/api/v3/datasets/WIKI/AAPL.csv?start_date=1985-05-01&end_date=1997-07-01&order=asc"
    #     print("I AM HERE")
    #     print(url_csv_file)
        


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404