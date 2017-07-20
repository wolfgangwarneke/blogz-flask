from flask import request, redirect, render_template, session, flash

from app import app, db
from models import User

@app.route("/")
def index():
    # encoded_error = request.args.get("error")
    return render_template('base.html', helloworld="Hello World")

@app.route("/login")
def login():
    pass

@app.route("/logout")
def logout():
    pass

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template('register.html')

@app.route("/dbinit")
def dbinit():
    db.drop_all()
    db.create_all()
    return "DB INIT!"

if __name__ == "__main__":
    print("Hello World")
    app.run()
