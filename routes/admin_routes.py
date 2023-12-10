from flask import Blueprint, jsonify, request
from config.helpers import MensajeResultados, getIDUserByName, runCommand
from scripts.uso_real_recursos import monitorear_uso_recursos
from services.userBDService import UserBDService

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/deleteUser',methods=['GET'])
def deleteUser():
	name=request.args.get("name")
	idCreated=getIDUserByName(name)
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