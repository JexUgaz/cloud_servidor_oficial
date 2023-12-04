import platform
from flask import Flask
from routes.admin_routes import admin_routes
from routes.user_routes import user_routes

app= Flask(__name__)
app.register_blueprint(admin_routes, url_prefix='/admin')
app.register_blueprint(user_routes, url_prefix='/user')

if __name__=="__main__":
	sys_op= platform.system()
	if sys_op=="Linux":
		app.run(debug=True,host='10.0.10.2',port=1800)
	elif sys_op=="Windows":
		app.run(debug=True,port=1800)
