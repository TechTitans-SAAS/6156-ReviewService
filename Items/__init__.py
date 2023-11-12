from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
# app.config["SECRET_KEY"] = "somekey"
app.config["MONGO_URI"] = "mongodb://localhost:27017/Items"

# mongodb database
mongodb_client = PyMongo(app)
db = mongodb_client.db

from Items import routes