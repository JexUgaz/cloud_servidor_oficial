from flask import Blueprint, jsonify, request
from config.helpers import MensajeResultados, getIDUserByName, runCommand
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