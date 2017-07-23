import json

from flask import request, redirect, render_template, session, flash, url_for
from sqlalchemy import exc, func

from app import app, db
from models import User, Post
from hashutils import make_pw_hash, check_pw_hash

# helper functions...
def get_current_user():
    try:
        current_username = session['username']
        return get_user(current_username)
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

def user_logged_in(username):
    try:
        current_username = session['username']
        return current_username == username
    except KeyError:
        print('No one is logged in right now')
        return False


# HOME ROUTE

@app.route("/")
@app.route("/home")
def index():
    users = User.query.limit(20).all()
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
        if user and check_pw_hash(password, user.password):
            session['username'] = user.username
            flash("Successfully logged in as {}.".format(user.username), "success")
            return redirect("/user/{}".format(user.username))
        else:
            flash("User not found.", "error")
            return render_template('login.html')

@app.route("/logout")
def logout():
    try:
        del session['username']
        flash("Log in again?", "suggestion")
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
            new_user = User(username, make_pw_hash(password))
            db.session.add(new_user)
            try:
                db.session.commit()
                flash("Registered as {}".format(new_user.username), "success")
                return render_template("login.html")
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

@app.route("/register/ajax", methods=["POST"])
def register_AJAX():
    username = request.form['username']
    password = request.form['password']
    password_confirm = request.form['password-confirm']
    if password == password_confirm and not User.query.filter_by(username=username).first() and len(username) > 3:
        new_user = User(username, make_pw_hash(password))
        db.session.add(new_user)
        try:
            db.session.commit()
            flash("Registered as {}".format(new_user.username), "success")
            data = {"name": new_user.username}
            return json.dumps(data)
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

@app.route("/post/<int:id>/update", methods=["POST"])
def update_post(id):
    try:
        publish = request.form['publish']
        post = Post.query.filter_by(id=id).first()
        if post:
            post.published = not post.published
            db.session.commit()
            return redirect("/post/{}".format(id))
        else:
            flash("Post not found", "error")
            return redirect('/')

    except AttributeError:
        return "can't publish or unpublish..."

# PUBLIC BROWSING ROUTES

@app.route("/posts")
def all_posts():
    posts = Post.query.filter_by(published=True).all()
    return render_template('posts.html', posts=posts)

@app.route("/post/<int:id>")
def post(id):
    post = Post.query.filter_by(id=id).first()
    if post:
        if not user_logged_in(post.owner.username):
            post.visits += 1
            db.session.commit()
        return render_template('post.html', post=post)
    else:
        flash("Post not found", "error")
        return redirect("/")

@app.route("/users")
def all_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route("/user/<username>")
def user(username):
    user = get_user(username)
    return render_template('posts.html', posts=user.posts, author=user.username)

@app.route("/search")
def search():
    query = request.args.get("query")
    if not query:
        return render_template('search.html')
    else:
        user_results = User.query.filter(func.lower(User.username) == func.lower(query)).all()
        post_results = Post.query.filter_by(published=True).filter(func.lower(Post.title) == func.lower(query)).all()
        args = {"query": query}
        if user_results:
            args["users"] = user_results
        if post_results:
            args["posts"] = post_results
        return render_template('search.html', **args)


# DEVELOPMENT ROUTES
# NEVER PUT THIS INTO PRODUCTION!!!

@app.route("/dbinit")
def dbinit():
    db.drop_all()
    db.create_all()
    return "DB INIT!"


if __name__ == "__main__":
    print("Hello World")
    app.run()
