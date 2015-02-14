from flask import Flask, url_for, render_template, request, flash, redirect, session
from app import app
# from .forms import LoginForm
from forms import RegisterForm, LoginForm, EditProfileForm
from sqlalchemy.sql import func
from models import db, User


@app.route('/')
@app.route('/index')
def index():
	if 'monkeyname' in session:
		return redirect(url_for('profile', monkeyname=session['monkeyname']))
	return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()

	if 'monkeyname' in session:
		return redirect(url_for('profile', monkeyname=session['monkeyname']))

	if request.method == 'POST':
		if form.validate() == False:
			print "wtf"
			return render_template('register.html', form=form)
		else:
			newuser = User(form.monkeyname.data, form.age.data, form.email.data, form.password.data)
			db.session.add(newuser)
			db.session.commit()
			session['monkeyname'] = newuser.monkeyname
			return redirect(url_for('profile', monkeyname=newuser.monkeyname))

	elif request.method == 'GET':
		return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if 'monkeyname' in session:
		return redirect(url_for('profile', monkeyname=session['monkeyname']))
   
	if request.method == 'POST':
		if form.validate() == False:
			return render_template('login.html', form=form)
		else:
			session['monkeyname'] = form.monkeyname.data
			return redirect(url_for('profile', monkeyname=session['monkeyname'], edit=1))
	             
	elif request.method == 'GET':
		return render_template('login.html', form=form)



@app.route('/logout')
def logout():
	if 'monkeyname' not in session:
		return redirect(url_for('login'))

	session.pop('monkeyname', None)
	return redirect(url_for('index'))



@app.route('/profile/<monkeyname>/')
@app.route('/profile/<monkeyname>/<int:page>')
def profile(monkeyname, page=1):
	if 'monkeyname' not in session:
		return redirect(url_for('login'))
 
  	# get the current user
	c_user = User.query.filter_by(monkeyname = session['monkeyname']).first()	
	# get the requested user
	r_user = User.query.filter_by(monkeyname=monkeyname).first()

  	if c_user is None:
  		return redirect(url_for('login'))
  	# dont allow editing if not own profile
  	elif monkeyname != c_user.monkeyname:
		return render_template('profile.html', user=r_user, edit=0, c_user=c_user)
	else:
		# get the shared bananas
		shared_bananas = c_user.shared_bananas.paginate(page,5,False)
		return render_template('profile.html', user=c_user, edit=1, shared_bananas=shared_bananas)



@app.route('/profile/<monkeyname>/edit/', methods=['GET', 'POST'])
def edit_profile(monkeyname):
	if 'monkeyname' not in session:
		return redirect(url_for('login')) 
	# get the current user
	user = User.query.filter_by(monkeyname = session['monkeyname']).first()
 	# set default values	
	form = EditProfileForm(monkeyname=user.monkeyname, age=user.age, email=user.email)

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('edit.html', form=form, user=user)
		else:
			# update values if they have changed and are not empty
 			if form.monkeyname.data:
 				user.monkeyname = form.monkeyname.data
 			if form.email.data:
 				user.email = form.email.data
 			if form.age.data:
 				user.age = form.age.data
 			if form.avatar.data:
 				user.avatar = form.avatar.data

			db.session.commit()
			session['monkeyname'] = user.monkeyname	#update the correct email to session
			flash('Profile info saved')
			return redirect(url_for('profile', monkeyname=user.monkeyname))

	elif request.method == 'GET':
		# get the requested user
		r_user = User.query.filter_by(monkeyname=monkeyname).first()
		# check if the monkey exists
		if r_user is None:
			return render_template('profile.html', user=user, edit=1)
		# dont allow editing if not own profile
		if r_user.monkeyname != session['monkeyname']:
			return render_template('profile.html', user=r_user, edit=0)
		return render_template('edit.html', form=form, user=user)


@app.route('/profile/<monkeyname>/delete/')
def delete_profile(monkeyname):
	if 'monkeyname' not in session:
		return redirect(url_for('login'))

	# get the current user
	c_user = User.query.filter_by(monkeyname = session['monkeyname']).first()	

	if c_user is None:
  		return redirect(url_for('login'))
  	# dont allow deleting if not own profile
  	elif monkeyname != c_user.monkeyname:
		return render_template('jungle.html')
	else:
		session.pop('monkeyname', None)
		db.session.delete(c_user)
		db.session.commit()
		return redirect(url_for('index'))



@app.route('/jungle')
@app.route('/jungle/<int:page>')
def jungle(page=1):

	# get the current user
	c_user = User.query.filter_by(monkeyname = session['monkeyname']).first()	

	value = request.args.get('sort','')
	# remember the sort parameter
	if value:
		sort_param = value
	else:
		sort_param = "name"		#default

	if sort_param == "name":
		# exclude the current user and sort by monkeyname
		monkeys = User.query.filter(User.monkeyname != session['monkeyname']).order_by(func.lower(User.monkeyname)).paginate(page,10,False)
	    	return render_template('jungle.html', monkeys=monkeys, sort_param=sort_param, c_user=c_user)
	elif sort_param == "bestfriend":
		# exclude the current user and sort by name of bestfriend
		monkeys = User.query.filter(User.monkeyname != session['monkeyname']).order_by(func.lower(User.best_friend)).paginate(page,10,False)
	    	return render_template('jungle.html', monkeys=monkeys, sort_param=sort_param, c_user=c_user)
	elif sort_param == "bananas":
		# exclude the current user and sort by amount of shared bananas
		monkeys = User.query.filter(User.monkeyname != session['monkeyname']).order_by(User.num_shared_bananas.desc()).paginate(page,10,False)
		return render_template('jungle.html', monkeys=monkeys, sort_param=sort_param, c_user=c_user)
	# else:
	# 	# exclude the current user
	# 	monkeys = User.query.filter(User.monkeyname != session['monkeyname']).paginate(page,5,False)
	#     	return render_template('jungle.html', monkeys=monkeys)



@app.route('/add/<monkeyname>')
def add_best_friend(monkeyname):
	# get the logged in user
	if 'monkeyname' not in session:
		return redirect(url_for('login'))

	# get the current user
	c_user = User.query.filter_by(monkeyname = session['monkeyname']).first()
	# user to add as best friend
	user = User.query.filter_by(monkeyname=monkeyname).first()

	if user is None:
		flash('User %s not found.' % monkeyname)
		return redirect(url_for('profile', monkeyname=c_user.monkeyname))
	if user == c_user:
		flash('You can\'t be best friends with yourself!')
		return redirect(url_for('profile', monkeyname=c_user.monkeyname))
	u = c_user.add_best_friend(user)
	if u is None:
		flash('Cannot ' + monkeyname + ' as best friend.')
		return redirect(url_for('profile', monkeyname=user.monkeyname))

	db.session.add(u)
	db.session.commit()
	flash(monkeyname + ' is now your best friend!')
	return redirect(url_for('profile', monkeyname=user.monkeyname))



@app.route('/remove/<monkeyname>')
def remove_best_friend(monkeyname):
	# get the logged in user
	if 'monkeyname' not in session:
		return redirect(url_for('login'))

	# get the current user
	c_user = User.query.filter_by(monkeyname = session['monkeyname']).first()
	# best friend to remove
	user = User.query.filter_by(monkeyname=monkeyname).first()

	if user is None:
		flash('User %s not found.' % monkeyname)
		return redirect(url_for('profile', monkeyname=c_user.monkeyname))
	if user == c_user:
		flash('You are not your own best friend!')
		return redirect(url_for('profile', monkeyname=c_user.monkeyname))
	u = c_user.remove_best_friend(user)
	if u is None:
		flash('Cannot remove ' + monkeyname + ' as best friend.')
		return redirect(url_for('profile', monkeyname=c_user.monkeyname))

	db.session.add(u)
	db.session.commit()
	flash('You have removed your best friend: ' + monkeyname + '!')
	return redirect(url_for('profile', monkeyname=c_user.monkeyname))


def redirect_url(default='profile'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


@app.route('/share/<monkeyname>')
def share_banana(monkeyname):

	# get the logged in user
	if 'monkeyname' not in session:
		return redirect(url_for('login'))

	# get the current user
	c_user = User.query.filter_by(monkeyname = session['monkeyname']).first()
	# user to share banana with
	user = User.query.filter_by(monkeyname=monkeyname).first()

	if user is None:
		flash('User %s not found.' % monkeyname)
		return redirect(url_for('jungle'))
	if user == c_user:
		flash('You can\'t share banana yourself!')
		return redirect(url_for('jungle'))
	u = c_user.share_banana(user)
	if u is None:
		flash('Cannot share banana ' + monkeyname + '.')
		return redirect(url_for('jungle'))

	db.session.add(u)
	db.session.commit()
	flash('You have shared your banana with the ' + monkeyname + '!')
	#return redirect(redirect_url())
	return redirect(url_for('profile', monkeyname=user.monkeyname))




@app.route('/unshare/<monkeyname>')
def unshare_banana(monkeyname):

	# get the logged in user
	if 'monkeyname' not in session:
		return redirect(url_for('login'))

	# get the current user
	c_user = User.query.filter_by(monkeyname = session['monkeyname']).first()
	# user to share banana with
	user = User.query.filter_by(monkeyname=monkeyname).first()

	if user is None:
		flash('User %s not found.' % monkeyname)
		return redirect(url_for('profile', monkeyname=c_user.monkeyname))
	if user == c_user:
		flash('You can\'t unshare banana yourself!')
		return redirect(url_for('profile', monkeyname=c_user.monkeyname))
	u = c_user.unshare_banana(user)
	if u is None:
		flash('Cannot unshare banana with ' + monkeyname + '.')
		return redirect(url_for('profile', monkeyname=c_user.monkeyname))

	db.session.add(u)
	db.session.commit()
	flash('You have stopped sharin your banana with ' + monkeyname + '.')
	#return redirect(redirect_url())
	return redirect(url_for('profile', monkeyname=user.monkeyname))



