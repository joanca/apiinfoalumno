from flask import render_template, request, redirect, session, url_for, jsonify
from google.appengine.api import memcache

def login():
	if 'username' and 'password' in session:
		return redirect(url_for('home'))

	elif request.method == 'POST':
		session['username'] = request.form['username']
		session['password'] = request.form['password']

		return redirect(url_for('home'))

	else:
		return 'Login requerido'

def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login'))

def home():
	if 'username' and 'password' in session:
		info = memcache.get('info-%s' % session['username'])
		if not info:
			import infoda
			infoalumno = infoda.Infoda(session['username'], session['password'])
			info = infoalumno.getInfo()
			info = jsonify(alumno=info)

			memcache.add('info-%s' % session['username'], info, 60*60)

		return info

	else:
		return redirect(url_for('login'))

def curricular():
	if 'username' and 'password' in session:
		info = memcache.get('info-%s' % session['username'])
		if not info:
			import infoda
			infoalumno = infoda.Infoda(session['username'], session['password'])
			info = infoalumno.getInfo()
			info = jsonify(alumno=info)

			memcache.add('info-%s' % session['username'], info, 60*60)

		return info

	else:
		return redirect(url_for('login'))

def ramo(idasig=None):
	if 'username' and 'password' in session:
		if idasig is not None:
			materiales = memcache.get('materiales-%s-%s' % (session['username'], idasig))
			if not materiales:
				import infoda
				infoalumno = infoda.Infoda(session['username'], session['password'])
				materiales = infoalumno.getMateriales(idasig)
				materiales = jsonify(materiales=materiales)

				memcache.add('materiales-%s-%s' % (session['username'], idasig), materiales, 60*60)

			return materiales

		else:
			return redirect(url_for('home'))

	else:
		return redirect(url_for('login'))

def notas(idasig=None):
	if 'username' and 'password' in session:
		if idasig is not None:
			notas = memcache.get('notas-%s-%s' % (session['username'], idasig))
			if not notas:
				import infoda
				infoalumno = infoda.Infoda(session['username'], session['password'])
				notas = infoalumno.getNotas(idasig)
				notas = jsonify(notas)

				memcache.add('notas-%s-%s' % (session['username'], idasig), notas, 60*60)

			return notas

	else:
		return redirect(url_for('login'))


############
# Desarrollo
############

#def loginpage():
#	if 'username' and 'password' in session:
#		return redirect(url_for('home'))
#
#	else:
#		template = '''
#		<form action="/login/" method="post">
#			<input name="username" type="text">
#			<input name="password" type="password">
#			<input type="submit" value="login">
#		</form>
#		'''
#		return template