from flask import render_template

from apiinfoda import app
from apiinfoda import views

# Home login (desarrollo)
#app.add_url_rule('/', 'loginpage', view_func=views.loginpage)

# Login
app.add_url_rule('/', 'login', view_func=views.login, methods=['GET', 'POST'])

# Logout
app.add_url_rule('/logout/', 'logout', view_func=views.logout)

# Home
app.add_url_rule('/home/', 'home', view_func=views.home)

# Curricular
app.add_url_rule('/curricular/', 'curricular', view_func=views.curricular)

# Ramo individual
app.add_url_rule('/ramo/<idasig>/', 'ramo', view_func=views.ramo)

# Notas
app.add_url_rule('/ramo/<idasig>/notas/', 'notas', view_func=views.notas)

## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500