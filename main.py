from flask import request, redirect, render_template, session, flash, url_for
from sqlalchemy import exc

from app import app, db
from models import User, Post

# helper functions...
def get_current_user():
    try:
        current_username = session['username']
        get_user(current_username)
    except KeyError:
        flash("No one is logged in", "server error")
        print("No one is logged in.")

def get_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return user
    else:
        flash("User not found", "server error")
        print("No user by that name found.")

# HOME ROUTE

@app.route("/")
@app.route("/home")
def index():
    users = User.query.limit(5).all()
    # encoded_error = request.args.get("error")
    return render_template('home.html', users=users)

# USER REGISTRATION/LOGIN ROUTES

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            session['username'] = user.username
            return "You are logged in now as {}.".format(user.username)
        else:
            return render_template('login.html', helloworld="NOT FOUND")

@app.route("/logout")
def logout():
    try:
        del session['username']
    except KeyError:
        flash("You are already logged out!", "error")
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password-confirm']
        if password == password_confirm and not User.query.filter_by(username=username).first() and len(username) > 3:
            # TODO create user
            new_user = User(username, password)
            db.session.add(new_user)
            try:
                db.session.commit()
                return "Registered as {}".format(new_user.username)
            except exc.SQLAlchemyError:
                flash("Unable to add user", "error")
                # TODO return form values
                return render_template('register.html')
        else:
            if User.query.filter_by(username=username).first():
                flash("User already exists")
                return render_template('register.html')
            if len(password) <= 6:
                flash("Password must be at least 6 characters.", "error")
            if not password == password_confirm:
                flash("Password confirmation must match password.", "error")
            if len(username) <= 3:
                flash("Username must be at least 3 characters", "error")
            return render_template('register.html')
    else:
        return render_template('register.html')

# USER SPECIFIC ROUTES

@app.route("/user/<username>/newpost", methods=["GET", "POST"])
def new_post(username):
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        if title and content:
            new_post = Post(title, content, get_current_user())
            db.session.add(new_post)
            db.session.commit()
            return redirect('/')
    else: # GET REQUEST
        if username == session['username']:
            return render_template('createpost.html')
        else:
            flash("You are not logged in as {}.".format(username), "error")
            return redirect(url_for('/users/{}'.format(username)))

# PUBLIC BROWSING ROUTES

@app.route("/posts")
def all_posts():
    posts = Post.query.filter_by(published=True).all()
    return render_template('posts.html', posts=posts)

@app.route("/users")
def all_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route("/user/<username>")
def user(username):
    user = get_user(username)
    return render_template('posts.html', posts=user.posts, author=user.username)


# DEVELOPMENT ROUTES

@app.route("/dbinit")
def dbinit():
    db.drop_all()
    db.create_all()
    return "DB INIT!"

if __name__ == "__main__":
    print("Hello World")
    app.run()
