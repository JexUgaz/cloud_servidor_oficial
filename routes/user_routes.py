import random
import subprocess
from flask import Blueprint, jsonify, request
from config.globals import InfraestructuraGlobal
from config.helpers import MensajeResultados, find_available_portVNC, generar_mac, generateNewIDVLan, runCommand
from createVM import init_VM
from entities.SliceEntity import SliceEntity
from entities.TopologiaEntity import TopologiaEntity
from entities.VirtualMachineEntity import VirtualMachineEntity
from services.imageBDService import ImageBDService
from services.sliceBDService import SliceBDService
from services.subredesBDService import SubredesBDService
from services.topologiaBDService import TopologiaBDService
from services.userBDService import UserBDService
from slice_DHCP import init_DHCP

user_routes = Blueprint('user_routes', __name__)
#Datos de conexión SSH
hosts = ['10.0.0.30','10.0.0.40','10.0.0.50']

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
	out=runCommand("sh -c \". ~/env-scripts/admin-openrc;openstack image list | grep -w '"+nombre+"' | awk '{print $4}'\"")
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
			return jsonify({'result':MensajeResultados.success,'msg':'Se creó exitosamente la imagen!','path':path})

@user_routes.route('/deleteImage',methods=['GET'])
def deleteImage():
	idImage=request.args.get('idImage')
	image=ImageBDService.getImageById(idImage=idImage)
	if image is None:
		return jsonify({'result':MensajeResultados.failed,'msg':'Ocurrió un error!'})
	elif image.id is None:
		return jsonify({'result':MensajeResultados.failed,'msg':f'No existe una imagen con el id: {idImage}'})
	else:
		result=ImageBDService.deleteImage(idImage=image.id)
		if(result):		
			runCommand(f"rm -f {image.path}")
			runCommand(f"sh -c '. ~/env-scripts/admin-openrc;openstack image delete {image.nombre}'")
			return jsonify({'result':MensajeResultados.success,'msg':f'Se eliminó exitosamente la imagen {image.nombre}'})
		else:
			return jsonify({'result':MensajeResultados.failed,'msg':'Error en la BD ocurrido!'})

@user_routes.route('/getUserById',methods=['GET'])
def getUserById():
	idUser=request.args.get("idUser")
	user=UserBDService.getUserById(id=idUser)
	if(user is None):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':'Ups! Ocurrió un error'
		})
	elif (user.id is None):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':f'No existe el usuario con el id {idUser}'
		})
	else:
		return jsonify({
			'result':MensajeResultados.success,
			'msg':'Se encontró exitosamente al usuario!',
			'user':user.to_dict()
		})

@user_routes.route('/getImagesByUser',methods=['GET'])
def getImagesByUser():
	idUser=request.args.get("idUser")
	imagenes=ImageBDService.getImagesByUser(idUser=idUser)

	if(imagenes is None):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':'Ups! Ocurrió un error'
		})
	elif (len(imagenes) == 0):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':f'El usuario: "{idUser}" no tiene imagenes!'
		})
	else:
		return jsonify({
			'result':MensajeResultados.success,
			'msg':'Se encontró exitosamente las imágenes!',
			'imagenes':imagenes
		})

@user_routes.route('/getAllTopologias',methods=['GET'])
def getAllTopologias():
	topologias=TopologiaBDService.getAllTopologias()

	if(topologias is None):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':'Ups! Ocurrió un error'
		})
	else:
		return jsonify({
			'result':MensajeResultados.success,
			'msg':'Se encontró exitosamente las topologías!',
			'topologias':topologias
		})


@user_routes.route('/setNewSlice',methods=['POST'])
def setNewSlice():
	#DEBEMOS HACER QUE LA RED TENGA MASCAA /29, máximo de 5 VMs
	
	data = request.json

	slice_entity = SliceEntity(
        id_vlan=data.get('id_vlan',None),
        nombre=data.get('nombre'),
        vms=[VirtualMachineEntity(**vm) for vm in data.get('vms', [])],
        nombre_dhcp=data.get('nombre_dhcp',None),
        topologia=TopologiaEntity(**data.get('topologia', [])[0]),
        infraestructura=data.get('infraestructura',None),
        fecha_creacion=data.get('fecha_creacion',None),
        usuario_id=data.get('usuario_id'),
        subred=data.get('subred',None)
    )
	new_id_vlan=generateNewIDVLan()
	name_dhcp=f"ns-dhcp-{new_id_vlan}"
	id_subred,subred=SubredesBDService.getRandomSubredDesactivado() #Hay que activar la subred
	result=SliceBDService.setNewSlice(new_id_vlan=new_id_vlan,cnt_nodos= len(slice_entity.vms),nombre_dhcp= name_dhcp,id_topologia=slice_entity.topologia.id,id_infraestructura=InfraestructuraGlobal.linux ,id_usuario=slice_entity.usuario_id,id_subred= id_subred,nombre=slice_entity.nombre )
	if result:
		init_DHCP(vlan_id=new_id_vlan,dir_net=subred)
		ports=[]
		ips_host=[]
		#2 VMs hasta 5 VMs
		starting_port=5901
		for vm in slice_entity.vms:
			ubicacion=random.randint(0, 2)
			port_vnc=find_available_portVNC(starting_port)			
			mac_addr=generar_mac()
			output=init_VM(vlan_id=new_id_vlan,size_ram=vm.sizeRam,id_worker=ubicacion,path=vm.imagen[0]['path'],mac_addr=mac_addr)			
			stdout_value = output['stdout'].strip()  # Elimina el carácter de nueva línea
			port_vnc_worker = int(stdout_value)

			subprocess.Popen(f"ssh -f -N -L {port_vnc+5900}:localhost:{port_vnc_worker+5900} ubuntu@{hosts[ubicacion]}&",shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

			ports.append(port_vnc+5900)
			ips_host.append(hosts[ubicacion])
			starting_port=port_vnc+5900+1


		return jsonify({
			'result':MensajeResultados.success,
			'msg':'Creado exitosamente!',
			'idSlice':new_id_vlan,
			'ports':ports,
			'hosts':ips_host
		})
	else:
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':'Hubo un error!'
		})
