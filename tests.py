import os
import unittest

from flask.ext.sqlalchemy import SQLAlchemy

from app import app, db
from app.models import User

class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/monkey-friends-test'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register(self, monkeyname, age, email, password):
        return self.app.post('/register', data=dict(
            monkeyname=monkeyname,
            age=age,
            email=email,
            password=password
        ), follow_redirects=True)

    def login(self, monkeyname, password):
        return self.app.post('/login', data=dict(
            monkeyname=monkeyname,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)


    def test_register_login_logout(self):
        # successful register
        rv = self.register('test', 22, 'test@gmail.com', 'test')
        assert 'profile' in rv.data
        # successful logout
        rv = self.logout()
        assert 'index' in rv.data
        # failed login
        rv = self.login('test123@gmail.com', 'random')
        assert 'login' in rv.data
        # successful login
        rv = self.login('test', 'test')
        assert 'profile' in rv.data
        self.logout()
        # register failed --> negative age
        rv = self.register('test', -22, 'test2@gmail.com', 'test')
        assert 'enter a reasonable positive age' in rv.data
        # register failed --> invalid email
        rv = self.register('test', 22, 'dummy', 'test')
        assert 'enter your email address' in rv.data
        # register failed --> too long name
        rv = self.register('toooooooolooooooooongnameeeeeee', 22, 'test@gmail.com', 'test')
        assert "name is too long" in rv.data
        # register failed --> email taken
        rv = self.register('test', 22, 'test@gmail.com', 'test')
        assert 'email is already taken' in rv.data


    def test_password_generation(self):
        u = User('testuser', 20, 'test@email.com', 'testpassword')
        assert u.check_password('testpassword')
        # change password
        u.set_password('newpassword')
        assert u.check_password('newpassword')


    def test_avatar(self):
        u = User('testuser', 20, 'test@email.com', 'testpassword')
        db.session.add(u)
        db.session.commit()
        #test that user has avatar (default=1)
        assert u.avatar == 1
        # change avatar
        u.avatar = 3
        db.session.commit()
        assert u.avatar == 3


    def test_banana_sharing(self):
        u1 = User(monkeyname='oranki', age=30, email='john@example.com', password="test1")
        u2 = User(monkeyname='apina', age=40, email='susan@example.com', password="test2")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unshare_banana(u2) is None
        u = u1.share_banana(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.share_banana(u2) is None
        assert u1.is_sharing_banana(u2)
        assert u1.shared_bananas.count() == 1
        assert u1.shared_bananas.first().monkeyname == 'apina'
        assert u2.banana_givers.count() == 1
        assert u2.banana_givers.first().monkeyname == 'oranki'
        u = u1.unshare_banana(u2)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert not u1.is_sharing_banana(u2)
        assert u1.shared_bananas.count() == 0
        assert u2.banana_givers.count() == 0


    def test_best_friend(self):
        u1 = User(monkeyname='paviaani', age=20, email='paviaani@example.com', password="paviaani")
        u2 = User(monkeyname='gorilla', age=50, email='gorilla@example.com', password="gorilla")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.best_friend is None
        # add best friend
        u = u1.add_best_friend(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.best_friend == u2.monkeyname
        # remove best friend
        u1.remove_best_friend(u2)
        assert u1.best_friend is None

    
if __name__ == '__main__':
    unittest.main()