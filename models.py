from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(2000))
    published = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    visits = db.Column(db.Integer)

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.published = False
        self.owner = owner
        self.visits = 0

    def __repr__(self):
        return '<Post "%r">' % self.title

    def publish(self):
        self.published = True

    def unpublish(self):
        self.published = False
