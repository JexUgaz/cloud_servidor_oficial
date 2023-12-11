from flask import Blueprint, jsonify, request
from config.helpers import MensajeResultados, generateNewPass, getIDOpenstackUserByName, runCommand, sendMail
from scripts.uso_real_recursos import monitorear_uso_recursos
from services.userBDService import UserBDService

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/deleteUser',methods=['GET'])
def deleteUser():
	name=request.args.get("name")
	idCreated=getIDOpenstackUserByName(name)
	runCommand(f"sh -c '. ~/env-scripts/admin-openrc;openstack user delete --domain default {name}'")
	UserBDService.deleteUserByID(idCreated)
	return jsonify({'result':MensajeResultados.success,'msg':'Usuario eliminado exitosamente!'})

@admin_routes.route('/listUser',methods=['GET'])
def listUser():
	usuarios=UserBDService.getUsuarios()
	return jsonify({'result':MensajeResultados.success,'usuarios':usuarios})

@admin_routes.route('/getMonitoreoRecursos',methods=['GET'])
def getMonitoreoRecursos():
	filas_memoria_consolidada_matrix,filas_uso_sistema_consolidado_matrix=monitorear_uso_recursos()
	return jsonify({'result':MensajeResultados.success,'msg':'Exitoso!!','memoria_workers':filas_memoria_consolidada_matrix,'uso_sistema_workers':filas_uso_sistema_consolidado_matrix})


@admin_routes.route('/setNewUser',methods=['POST'])
def setNewUser():
	name=request.form.get('name') #Nombre del usuario a crear [STRING]
	rol=request.form.get('rol') #id del Rol del usuario (Administrador, Usuario) [INT]
	email=request.form.get('email') #Email para los correos [STRING]
	print(f"{name} {rol} {email}")
	user1=UserBDService.getUserByName(nombre=name)
	user2=UserBDService.getUserByEmail(email=email)
	if user1==None or user2==None:
		return jsonify({'result':MensajeResultados.failed,'msg':'Ocurrió un error!'})
	elif (user1!=None and user1.id==None) and (user2!=None and user2.id==None):
		#NO EXISTEN ENTONCES
		pswrd=generateNewPass() #Generamos una contraseña aleatoria
		runCommand(f"sh -c '. ~/env-scripts/admin-openrc;openstack user create --domain default --password {pswrd} {name}'")
		idCreated=getIDOpenstackUserByName(name)
		result=UserBDService.setNewUser(name,pswrd,email,rol,idCreated)
		if result:
			sendMail(receptor=email,subject="ACCESO HABILITADO - CLOUD HELP",msg='<!DOCTYPE html><html lang="es"><head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Bienvenido a CLOUD HELP</title> <style> body { font-family: \'Arial\', sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; display: flex; align-items: center; justify-content: center; height: 100vh; } .container { background-color: #fff; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); padding: 20px; text-align: center; } h1 { color: #333; } p { color: #666; } .credentials { background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-top: 15px; } </style></head><body><div class="container"> <h1>Bienvenido a CLOUD HELP</h1> <p>Te damos la bienvenida a nuestra plataforma de ayuda en la nube. A continuación, encontrarás tus credenciales de acceso:</p> <div class="credentials"> <p><strong>Usuario:</strong> '+name+'</p> <p><strong>Contraseña:</strong>'+pswrd+'</p> </div> <p>¡Gracias por elegir CLOUD HELP! Estamos emocionados de tenerte como parte de nuestra comunidad.</p></div></body></html>')
			return jsonify({'result':MensajeResultados.success,'msg':f'Usuario creado exitosamente!\nSe envió un correo al destinatario {email}','id':idCreated})
		else:
			return jsonify({'result':MensajeResultados.failed,'msg':'Ocurrió un error!'})
	else:
		return jsonify({'result':MensajeResultados.failed,'msg':'Nombre o email ya existen!'})
