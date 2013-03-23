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
		infoalumno = infoda.Infoda(session['username'], session['password'])
		info = infoalumno.getInfo()

		datos_alumno = dict(info=info)

		return jsonify(alumno=datos_alumno)

	else:
		return redirect(url_for('login'))

def curricular():
	if 'username' and 'password' in session:
		infoalumno = infoda.Infoda(session['username'], session['password'])
		info = infoalumno.getInfo()

		return jsonify(alumno=info)

	else:
		return redirect(url_for('login'))

def ramo(idasig=None):
	if 'username' and 'password' in session:
		infoalumno = infoda.Infoda(session['username'], session['password'])
		info = infoalumno.getInfo()

		datos_alumno = dict(
			nombre=info['nombre'],
			avatar=info['avatar'],
			carrera=info['carrera'])

		if idasig is not None:
			materiales = infoalumno.getMateriales(idasig)

			return jsonify(materiales=materiales, alumno=datos_alumno)

		
		else:
			return redirect(url_for('home'))

	else:
		return redirect(url_for('login'))

def notas(idasig=None):
	if 'username' and 'password' in session:
		infoalumno = infoda.Infoda(session['username'], session['password'])
		info = infoalumno.getInfo()

		datos_alumno = dict(
			nombre=info['nombre'],
			avatar=info['avatar'],
			carrera=info['carrera'])

		if idasig is not None:
			notas = infoalumno.getNotas(idasig)

			return jsonify(notas=notas, alumno=datos_alumno)

	else:
		return redirect(url_for('login'))
