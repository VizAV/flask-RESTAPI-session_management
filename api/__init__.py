from flask import Flask, g,jsonify
from flask_pymongo import PyMongo
from api.auth.routes import auth_module
app=Flask(__name__)
app.config.from_object('config')

mongo = PyMongo(app)

# THis is needed to give global access to the db and be able to put values in the db
@app.before_request
def before_request():
	# mongo.db.add_son_manipulator(UTF8Encoder())
	# mongo.db.add_son_manipulator(IDtoString())
	# mongo.db.add_son_manipulator(StringtoID())
	g.db = mongo.db
@app.route('/')
def index():
	return jsonify({"Message":"Hi"})

# REGISTER BLUEPRINTS
app.register_blueprint(auth_module)