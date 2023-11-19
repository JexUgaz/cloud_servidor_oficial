from flask import Flask,jsonify,request
import subprocess
from services.mysql_connect import MySQLConnect
from services.userBDService import UserBDService

app= Flask(__name__)

MySQLConnect.initialConnection()

def runCommand(command):
	result=subprocess.run("sudo "+command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	return result.stdout.strip()

@app.route('/setNewSlice',methods=['POST'])
def setNewSlice():
	#DEBEMOS HACER QUE LA RED TENGA MASCAA /29, máximo de 5 VMs
	idVlan='50' #La VLAN lo sacara el propio servidor de la BD, id del Slice
	
	idTopologia= request.form.get('idTopologia') # ID de la Topología
	idUser=request.form.get('idUser') #ID del usuario, por ahora no lo usamos
	n_Vms= request.form.get('n_Vms') # 4 : Número de VMs
	ubicaciones= request.form.getlist('ubicaciones') # 0,2, 0, 2 : WORKER1, WORKER3, WORKER1, WORKER3
	size_ram=request.form.getlist('size_ram') # 100,100,100,100 : 100Mbytes memoria RAM

	print(f"Topología: {idTopologia}")
	print(f"User: {idUser}")
	print(f"N° Vms: {n_Vms}")
	print(f"Ubicaciones: {ubicaciones}")
	print(f"Tamaño: {size_ram}")

	#runCommand(f'python3 slice_DHCP.py br-int {idVlan} 192.168.10.0/24 192.168.10.5 192.168.10.10')

	#2 VMs hasta 5 VMs
	#for i in range(len(ubicaciones)):
	#	runCommand(f'python3 createVM.py slice{idVlan}-vm{i} {idVlan} 50{i} {size_ram[i]} {ubicaciones[i]}')

	return jsonify({
		'msg':'Creado exitosamente!',
		'idSlice':'50',
		'ports':['6400','6401','6402','6403'],
		'hosts':['10.0.0.30','10.0.0.50','10.0.0.30','10.0.0.50']
	})
def _getIDUserByName(name):
	return runCommand(f"sh -c '. ~/env-scripts/admin-openrc;openstack user list' | grep '{name}'"+" | awk '{print $2}'")
	

@app.route('/setNewUser',methods=['POST'])
def setNewUser():
	name=request.form.get('name') #Nombre del usuario a crear [STRING]
	pswrd=request.form.get('pswrd') #Contraseña del usuario a crear [STRING]
	rol=request.form.get('rol') #id del Rol del usuario (Administrador, Usuario) [INT]
	email=request.form.get('email') #Email para los correos [STRING]
	runCommand(f"sh -c '. ~/env-scripts/admin-openrc;openstack user create --domain default --password {pswrd} {name}'")
	idCreated=_getIDUserByName(name)
	result=UserBDService.setNewUser(name,pswrd,email,rol,idCreated)
	if result:
		return jsonify({'result':'success','msg':'Usuario creado exitosamente!','id':idCreated})
	else:
		return jsonify({'result':'failed','msg':'Ocurrió un error!'})

@app.route('/deleteUser',methods=['GET'])
def deleteUser():
	name=request.args.get("name")
	idCreated=_getIDUserByName(name)
	runCommand(f"sh -c '. ~/env-scripts/admin-openrc;openstack user delete --domain default {name}'")
	UserBDService.deleteUserByID(idCreated)
	return jsonify({'result':'success','msg':'Usuario eliminado exitosamente!'})

@app.route('/authenticationUser',methods=['POST'])
def authenticationUser():
	name=request.form.get('name')
	pswrd=request.form.get('pswrd')
	print(f"Nombre y pass: {name} {pswrd}")
	result= UserBDService.getUserByCredentials(name=name,password=pswrd)
	if result==None:
		return jsonify({'result':'failed','msg':'Ocurrió un error!'})
	else: 
		return jsonify({'result':'success','msg':'Usuario encontrado exitosamente!','user':result})

if __name__=="__main__":
	app.run(debug=True,host='10.0.10.2',port=1800)
