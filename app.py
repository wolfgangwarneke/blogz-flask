from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from secret import SQLALCHEMY_DATABASE_URI, SECRET_KEY

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = SECRET_KEY
