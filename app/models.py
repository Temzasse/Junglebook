from werkzeug import generate_password_hash, check_password_hash
from app import db
from sqlalchemy.ext.hybrid import hybrid_property

banana_givers = db.Table('banana_givers',
    db.Column('giver_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('receiver_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    monkeyname = db.Column(db.String(64), index=True, unique=True)
    age = db.Column(db.Integer, index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    avatar = db.Column(db.Integer)
    best_friend = db.Column(db.String(64), index=True)
    pwdhash = db.Column(db.String(200))
    shared_bananas = db.relationship('User', 
                               secondary=banana_givers, 
                               primaryjoin=(banana_givers.c.giver_id == id), 
                               secondaryjoin=(banana_givers.c.receiver_id == id), 
                               backref=db.backref('banana_givers', lazy='dynamic'), 
                               lazy='dynamic')

    def __init__(self, monkeyname, age, email, password):
        self.monkeyname = monkeyname
        self.age = age
        self.email = email.lower()
        self.avatar = 1     #default value
        self.set_password(password)
     
    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
         return check_password_hash(self.pwdhash, password)

    def add_best_friend(self, user):
        self.best_friend = user.monkeyname
        return self

    def remove_best_friend(self, user):
        self.best_friend = None
        return self

    def share_banana(self, user):
        if not self.is_sharing_banana(user):
            self.shared_bananas.append(user)
            return self

    def unshare_banana(self, user):
        if self.is_sharing_banana(user):
            self.shared_bananas.remove(user)
            return self

    def is_sharing_banana(self, user):
        return self.shared_bananas.filter(banana_givers.c.receiver_id == user.id).count() > 0

    @hybrid_property
    def num_shared_bananas(self):
        return len(self.shared_bananas)

    @num_shared_bananas.expression
    def _num_shared_bananas_expression(cls):
        return (db.select([db.func.count(banana_givers.c.receiver_id).label("num_shared")])
                .where(banana_givers.c.giver_id == cls.id)
                .label("total_shared")
                )

    def __repr__(self):
        return '<User %r>' % (self.monkeyname)


