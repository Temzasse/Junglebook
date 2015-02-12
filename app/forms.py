from flask import session
from flask.ext.wtf import Form
from wtforms import StringField, HiddenField, BooleanField, IntegerField, TextField, SubmitField, TextAreaField, PasswordField
from wtforms import validators
from models import db, User


class LoginForm(Form):
	monkeyname = TextField("Your Monkey's name",  [validators.Required("Please enter your email address.")])
	password = PasswordField('Password', [validators.Required("Please enter a password.")])
	submit = SubmitField("Sign In")
   
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
 
 	def validate(self):
		if not Form.validate(self):
			return False
     
		user = User.query.filter_by(monkeyname = self.monkeyname.data).first()
		if user and user.check_password(self.password.data):
			return True
		else:
			self.monkeyname.errors.append("Invalid monkeyname or password")
			return False


class RegisterForm(Form):
	monkeyname = TextField("Name",  [validators.Required("Please enter your Monkey's name."), validators.Length(max=20, message="Your Monkey's name is too long.")])
	age = IntegerField("Age",  [validators.Required("Please enter your age."), validators.NumberRange(min=0, max=120, message="Please enter a reasonable positive age.")])
	email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
	password = PasswordField('Password', [validators.Required("Please enter a password.")])
	submit = SubmitField("Create account")
 
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
 
	def validate(self):
		if not Form.validate(self):
			return False
     
		email_taken = User.query.filter_by(email = self.email.data.lower()).first()
		if email_taken:
			self.email.errors.append("That email is already taken")
			return False

		monkeyname_taken = User.query.filter_by(monkeyname = self.monkeyname.data.lower()).first()
		if monkeyname_taken:
			self.monkeyname.errors.append("That name is already taken")
			return False
		else:
			return True



class EditProfileForm(Form):
	monkeyname = TextField("Monkey name",  [validators.Optional(), validators.Length(max=20, message="Your Monkey's name is too long.")])
	age = IntegerField("Age",  [validators.Optional(), validators.NumberRange(min=0, max=120, message="Please enter a reasonable positive age.")])
	email = TextField("Email",  [validators.Optional(), validators.Email("Please enter your email address.")])
	avatar = HiddenField("Avatar", [validators.Optional()])
	submit = SubmitField("Save")
 
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
 
	def validate(self):
		if not Form.validate(self):
			return False
     
		user_by_email = User.query.filter_by(email = self.email.data.lower()).first()
		user_by_monkeyname = User.query.filter_by(monkeyname = self.monkeyname.data.lower()).first()
		c_user = User.query.filter_by(monkeyname = session['monkeyname']).first()

		if user_by_email and user_by_email.email != c_user.email:
			self.email.errors.append("That email is already taken")
			return False
		if user_by_monkeyname and user_by_monkeyname.monkeyname != c_user.monkeyname:
			self.monkeyname.errors.append("That monkeyname is already taken")
			return False
		else:
			return True






