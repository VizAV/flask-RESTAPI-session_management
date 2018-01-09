from flask import Flask,jsonify,request
from flask_pymongo import PyMongo
import string,random
from email.mime.multipart import MIMEMultipart # to build email body, To and from parts
from email.mime.text import MIMEText           # to build email body, To and from parts
from utils import EmailHelper # to sent email to elient

app=Flask(__name__)
app.config['MONGO_DBNAME'] = 'vishwa_restDB'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/vishwa_restDB'
mongo = PyMongo(app)

@app.route('/')
def home():
	response = {'message': "Welcome to RESTAPI!"}
	return jsonify(response)

@app.route('/register', methods=['POST'])
def register():
    input = {
        'firstName': request.form.get('firstName'),
        'lastName': request.form.get('lastName'),
        'emailId': request.form.get('emailId'),
        'password': request.form.get('password')
    }

    # Check details
    if mongo.db.users.find({'emailId':input['emailId']}).count():
        response = {'message': 'User exists, please login or provide another Email ID', 'status_code': 409}
        return jsonify(response)



    # Try catch
    # Password encrptyion
    # Put in database
    mongo.db.users.insert({
        "firstName": input['firstName'],
        "lastName": input['lastName'],
        "emailId": input['emailId'],
        "password": input['password'],
        "verificationStatus":False,
        "emailToken":None
    })

    # verifyEmail

    alphabets = string.ascii_lowercase # Gets all the alphabets in lowercase

    # Generate random strings and make sure none of our existing users have it
    while True:
        emailToken = ''.join([random.choice(alphabets) for i in range(20)])
        if not mongo.db.users.find({"emailToken":emailToken}).count():
            break
    mongo.db.users.update({"emailId": input['emailId']}, {"$set": {"emailToken": emailToken}})

    # Setup a mailID and enable sending it

    msg = MIMEMultipart()  # initialising email content handler
    msg['From'] = 'vishwanath@gmail.com'
    msg['Subject'] = "Registration confirmation"
    body = "Hi,\n\nWelcome to Vishwa's test Proj"

    msg.attach(MIMEText(body, 'plain'))  # attching email body with the email content handler
    msg['To'] = input['emailId']
    text = msg.as_string()
    # email_helper = EmailHelper()
    # email_helper.send_mail(email, text)  # semding email with the mentioned parameters and email body
    # response = {'message': 'Please, check your mail and click on the activation link to verify your account',
    #             'status_code': 200}
    # return jsonify(response)

    output = {'response': "User registered"}
    return jsonify(output)

if __name__ == "__main__":
	app.run(host="0.0.0.0")