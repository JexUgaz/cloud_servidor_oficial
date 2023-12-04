from flask import Blueprint, jsonify, request
from config.helpers import MensajeResultados, getIDUserByName, runCommand
from services.imageBDService import ImageBDService
from services.userBDService import UserBDService

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/authenticationUser',methods=['POST'])
def authenticationUser():
	name=request.form.get('name')
	pswrd=request.form.get('pswrd')
	print(f"Nombre y pass: {name} {pswrd}")
	result= UserBDService.getUserByCredentials(name=name,password=pswrd)
	if result==None:
		return jsonify({'result':MensajeResultados.failed,'msg':'Ocurrió un error!'})
	else: 
		return jsonify({'result':MensajeResultados.success,'msg':'Usuario encontrado exitosamente!','user':result})
	

@user_routes.route('/setNewImage',methods=['POST'])
def setNewImage():
	#http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img
	link=request.form.get('link')
	idUser=request.form.get('idUser')
	nombre=request.form.get('nombre')
	print(f"Data: {nombre} | {idUser} | {link}")
	out=runCommand("sh -c \". ~/env-scripts/admin-openrc;openstack image list | grep -w '"+nombre+"' | awk '{print $4}'\"")
	print("LLEGAMOS HASTA ACA")
	print(f"Salida: {out}")
	if out:
		return jsonify({'result':MensajeResultados.failed,'msg':f'Ya existe una imagen con el nombre: {nombre}'})
	else:
		name_image = link.split("/")[-1] #cirros-0.4.0-x86_64-disk.img
		out2=runCommand(f"[ -e ~/imagenes/{idUser}/{name_image} ] && echo 'El archivo o directorio existe'")
		if out2:
			return jsonify({'result':MensajeResultados.failed,'msg':f'Ya existe descargado esta imagen: {name_image}'})
		else:
			runCommand(f"wget {link} && mkdir -p ~/imagenes/{idUser} && mv {name_image} ~/imagenes/{idUser}/")
			runCommand(f"sh -c '. ~/env-scripts/admin-openrc; glance image-create --name \"{nombre}\" --file ~/../home/ubuntu/imagenes/{idUser}/cirros-0.4.0-x86_64-disk.img --disk-format qcow2 --container-format bare --visibility=public'")
			path=runCommand(f'find / -type f -name "{name_image}" -path "*{idUser}*"')
			ImageBDService.setNewImage(path=path,nombre=nombre,usuario_id=idUser) #Guardamos en la BD MySQL
			return jsonify({'result':MensajeResultados.success,'msg':'Se descargó exitosamente!','path':path})


@user_routes.route('/setNewSlice',methods=['POST'])
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
		'result':MensajeResultados.success,
		'msg':'Creado exitosamente!',
		'idSlice':'50',
		'ports':['6400','6401','6402','6403'],
		'hosts':['10.0.0.30','10.0.0.50','10.0.0.30','10.0.0.50']
	})

@user_routes.route('/setNewUser',methods=['POST'])
def setNewUser():
	name=request.form.get('name') #Nombre del usuario a crear [STRING]
	pswrd=request.form.get('pswrd') #Contraseña del usuario a crear [STRING]
	rol=request.form.get('rol') #id del Rol del usuario (Administrador, Usuario) [INT]
	email=request.form.get('email') #Email para los correos [STRING]
	runCommand(f"sh -c '. ~/env-scripts/admin-openrc;openstack user create --domain default --password {pswrd} {name}'")
	idCreated=getIDUserByName(name)
	result=UserBDService.setNewUser(name,pswrd,email,rol,idCreated)
	if result:
		return jsonify({'result':MensajeResultados.success,'msg':'Usuario creado exitosamente!','id':idCreated})
	else:
		return jsonify({'result':MensajeResultados.failed,'msg':'Ocurrió un error!'})
