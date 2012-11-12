from bs4 import BeautifulSoup
from requests import session
import base64

from google.appengine.api import memcache

class Infoda():

	def __init__(self, user, passw):

		self.usuario = user
		self.password = passw

		data = {
			'action':	'login',
			'username':	'%s' % self.usuario,
			'clave':	'%s' % self.password
		}

		with session() as self.s:
			self.s.post('http://infoda.udec.cl/INFODA_ingreso.php', data=data)

	def getInfo(self):
		q = memcache.get('q-%s' % self.usuario)
		if not q:
			q = self.s.get('http://infoda.udec.cl/INFODA_contenido.php').content
			memcache.add('q-%s' % self.usuario, q, 60*60)
		html = BeautifulSoup(q)

		avatar = html.find_all('img', limit=2)
		avatar_url = 'http://infoda.udec.cl/'+avatar[1].get('src')

		avatar = memcache.get('avatar-%s' % self.usuario)
		if not avatar:
			avatar = 'data:image/pjpeg;base64,'+base64.b64encode(self.s.get(avatar_url).content)
			memcache.add('avatar-%s' % self.usuario, avatar, 60*60*24)

		nombre = html.find_all('b')[0].string

		r = memcache.get('r-%s' % self.usuario)
		if not r:
			r = self.s.get('http://infoda.udec.cl/INFODA_Curricular.php').content
			memcache.add('r-%s' % self.usuario, r, 60*60)
		html2 = BeautifulSoup(r, 'html5lib')
		html2 = str(html2.body).split('<script>')[-1].split('(')[1]

		datos_curricular = html2.split(',')

		matricula = datos_curricular[0]
		area_alumno = datos_curricular[1].split(');')[0].replace("'", '')

		parametros = {
			"vari": "mat_al=%s&area_al=%s" % (matricula, area_alumno)
		}

		d = memcache.get('d-%s' % self.usuario)
		if not d:
			c = self.s.post('http://infoda.udec.cl/INFODA_ncrpt.php', data=parametros)
			d = self.s.get('http://infoda.udec.cl/INFODA_infoCurricular.php?v='+c.content).content

			memcache.add('d-%s' % self.usuario, d, 60*60)

		datos_carrera = d.split(';')[18].split('<td>')[1].replace("</td>'", '').split()
		codigo_carrera = datos_carrera[0]
		carrera = datos_carrera[1:]
		carrera = ' '.join(carrera)

		str_carrera = d.split("';")

		estado_carrera = str_carrera[18].split('<td>')[1].replace("</td>", '')
		total_ramos = str_carrera[28].split('">')[1][3:].replace("</td>", '')
		promedio = str_carrera[30].split('">')[1].replace("</td>", '') # Promedio de asignaturas aprobadas
		creditos_aprobados = str_carrera[34].split(' : ')[1]
		creditos_reprobados = str_carrera[37].split(' : ')[1].replace("</td>", '')

		info_asignaturas = ''.join(str_carrera[59:-20])
		info_asignaturas = info_asignaturas.split("resultado+='<tr>")[1:]

		asignaturas = []

		for i in range(len(info_asignaturas)):

			info_asignatura = info_asignaturas[i].split("resultado+='<td")[1:]
			ramo = ' '.join(info_asignatura[3].split('">')[1].rsplit())
			creditos = info_asignatura[4].split('">')[1].split('<center>')[1].rsplit()[0].split('</center>')[0]
			nota = info_asignatura[5].split('">')[1].split('<center>')[1].rsplit()[0].split('</center>')[0]
			estado = info_asignatura[6].split('">')[1].split('<center>')[1].split('</center>')[0]
			codigo = info_asignatura[2].split('">')[1].split('<center>')[1].split('</center>')[0].replace(' ', '')

			c = dict(nombre=ramo, creditos=creditos, nota=nota, estado=estado, codigo=codigo)
			asignaturas.append(c)


		info = dict(nombre=nombre,
			avatar=avatar,
			matricula=matricula,
			codigo_carrera=codigo_carrera,
			carrera=carrera,
			asignaturas=asignaturas,
			estado_carrera=estado_carrera,
			total_ramos=total_ramos,
			promedio=promedio,
			creditos_reprobados=creditos_reprobados,
			creditos_aprobados=creditos_aprobados)

		return info

	def getMateriales(self, idasig=None):
		ramos = self.getInfo()['asignaturas']

		if idasig is None:
			datos_materiales = []
			for ramo in ramos:
				if ramo['estado'] == 'Sin Nota':
					v = memcache.get('v-%s' % ramo['codigo'])
					if not v:
						v = self.s.get('http://infoda.udec.cl/INFODA_verMaterialAlumno.php?cAsig='+ramo['codigo']).content
						memcache.add('v-%s' % ramo['codigo'], v, 60*60)

					html = v[87:].replace("'</script>", '')
					html = BeautifulSoup(html)

					materiales = html.find_all('a')

					info_materiales = memcache.get('materiales-%s-todo' % self.usuario)
					if not info_materiales:
						info_materiales = []

						for material in materiales:
							id_mat = material.get('idmat')
							nombre_mat = str(material).split('">')[1].split('</br>')[0]
							alt = material.get('alt') # Usado para comprobar si es un archivo o url

							if '<br>' in nombre_mat:
								nombre_mat = nombre_mat.replace('<br>', '')
							if '</a>' in nombre_mat:
								nombre_mat = nombre_mat.replace('</a>', '')
							if '<br/>' in nombre_mat:
								nombre_mat = nombre_mat.replace('<br/>', '')
							
							if 'Material' in alt:
								nick_profe = material.get('onclick').split('(')[2].replace('\\\'', '').replace(');', '').split(',')[1]
								parametros = {
									"vari": "idd=%s&loggg=%s&loggin=%s" % (id_mat, nick_profe, self.usuario)
								}

								c = self.s.post('http://infoda.udec.cl/INFODA_ncrpt.php', data=parametros)
								url = 'http://infoda.udec.cl/INFODA_muestraMaterial.php?v='+c.content

							else:
								url = material.get('href')

							d = dict(nombre=nombre_mat, url=url)
							info_materiales.append(d)
						memcache.add('materiales-%s-todo' % self.usuario, info_materiales, 60*60)

					p = dict(asignatura=ramo, materiales=info_materiales)
					datos_materiales.append(p)

			return datos_materiales

		else:
			datos_materiales = []
			for ramo in ramos:
				if ramo['codigo'] == idasig:
					v = memcache.get('v-%s-%s' % (self.usuario, ramo['codigo']))
					if not v:
						v = self.s.get('http://infoda.udec.cl/INFODA_verMaterialAlumno.php?cAsig='+ramo['codigo']).content
						memcache.add('v-%s-%s' % (self.usuario, ramo['codigo']), v, 60*60)
					html = v[87:].replace("'</script>", '')
					html = BeautifulSoup(html)		

					materiales = html.find_all('a')

					info_materiales = memcache.get('materiales-%s-%s' % (self.usuario, ramo['codigo']))
					if not info_materiales:
						info_materiales = []

						for material in materiales:
							id_mat = material.get('idmat')
							nombre_mat = str(material).split('">')[1].split('</br>')[0]
							alt = material.get('alt') # Usado para comprobar si es un archivo o url

							if '<br>' in nombre_mat:
								nombre_mat = nombre_mat.replace('<br>', '')
							if '</a>' in nombre_mat:
								nombre_mat = nombre_mat.replace('</a>', '')
							if '<br/>' in nombre_mat:
								nombre_mat = nombre_mat.replace('<br/>', '')
							
							if 'Material' in alt:
								nick_profe = material.get('onclick').split('(')[2].replace('\\\'', '').replace(');', '').split(',')[1]
								parametros = {
									"vari": "idd=%s&loggg=%s&loggin=%s" % (id_mat, nick_profe, self.usuario)
								}

								c = self.s.post('http://infoda.udec.cl/INFODA_ncrpt.php', data=parametros)
								url = 'http://infoda.udec.cl/INFODA_muestraMaterial.php?v='+c.content

							else:
								url = material.get('href')

							d = dict(nombre=nombre_mat, url=url)
							info_materiales.append(d)
						memcache.add('materiales-%s-%s' % (self.usuario, ramo['codigo']), info_materiales, 60*60)

					p = dict(asignatura=ramo, materiales=info_materiales)
					datos_materiales.append(p)

			return datos_materiales

	def getNotas(self, idasig=None):
		ramos = self.getInfo()['asignaturas']

		if idasig is not None:
			for ramo in ramos:
				if ramo['codigo'] == idasig:
					v = self.s.get('http://infoda.udec.cl/INFODA_verCalificaciones2.php?kEval=2&carr=0&cAsig='+ramo['codigo']).content

					html = v[85:]
					html = BeautifulSoup(html)

					datos = str(html).split('"td')[1:]

					info_notas = []

					for dato in datos[:-1]:
						evaluacion = dato.split('">')[3].split('</')[0].decode('utf-8').strip()
						nota = dato.split('">')[4].split('</')[0]
						fecha = dato.split('">')[2].split('</')[0]

						p = dict(evaluacion=evaluacion, nota=nota, fecha=fecha)
						info_notas.append(p)

					try:
						ev_rec = datos[-1].split('</')[1].decode('utf-8').split('<td>')[1]
						nota_ev_rec = datos[-1].split('">')[3].split('</')[0]
						recuperacion = dict(nota=nota_ev_rec, nombre=ev_rec)
					except IndexError:
						recuperacion = dict(nota='', nombre='')

					try:
						ev_final = datos[-1].split('</')[7].split('<b>')[1].replace(':', '')
						nota_ev_final = datos[-1].split('<b>')[2].split('</b>')[0]
						final = dict(nota=nota_ev_final, nombre=ev_final)
					except IndexError:
						final = dict(nota='', nombre='')

					notas = dict(asignatura=ramo, evaluaciones=info_notas, recuperacion=recuperacion, final=final)


					return notas