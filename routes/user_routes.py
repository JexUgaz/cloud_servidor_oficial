import json
import random
import subprocess
from flask import Blueprint, jsonify, request
from config.globals import InfraestructuraGlobal
from config.helpers import MensajeResultados, find_available_portVNC, generar_mac, generateNewIDVLan, runCommand
from createVM import init_VM
from entities.SliceEntity import SliceEntity
from entities.TopologiaEntity import TopologiaEntity
from entities.VirtualMachineEntity import VirtualMachineEntity
from scripts.limpiar_Slice import cleanWorker, kill_ssh_tunnel_processes, limpiarDHCP_Interfaces
from services.imageBDService import ImageBDService
from services.sliceBDService import SliceBDService
from services.subredesBDService import SubredesBDService
from services.topologiaBDService import TopologiaBDService
from services.userBDService import UserBDService
from services.virtualMachineBDService import VirtualMachineBDService
from services.zonaBDService import ZonaBDService
from slice_DHCP import init_DHCP

user_routes = Blueprint('user_routes', __name__)
#Datos de conexión SSH

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
			runCommand(f"sh -c '. ~/env-scripts/admin-openrc; glance image-create --name \"{nombre}\" --file ~/../home/ubuntu/imagenes/{idUser}/{name_image} --disk-format qcow2 --container-format bare --visibility=public'")
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


@user_routes.route('/getSlicesByUser',methods=['GET'])
def getSlicesByUser():
	idUser=request.args.get("idUser")
	slices=SliceBDService.getSlicesByUser(idUser)

	if(slices is None):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':'Ups! Ocurrió un error'
		})
	elif (len(slices) == 0):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':f'El usuario: "{idUser}" no tiene slices!'
		})
	else:
		return jsonify({
			'result':MensajeResultados.success,
			'msg':'Se encontró exitosamente las imágenes!',
			'slices':slices
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
	

@user_routes.route('/getAllVMs',methods=['GET'])
def getAllVirtualMachines():
	idSlice=request.args.get("idSlice")
	slice=SliceBDService.getSliceByID(idSlice)
	if(slice is None):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':'Ups! Ocurrió un error'
		})
	elif (slice.id_vlan is None):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':'No existe el slice!'
		})
	else:
		vms=VirtualMachineBDService.getVMBySlice(idSlice)
		vms_json=[vm.to_dict() for vm in vms]
		return jsonify({
				'result':MensajeResultados.success,
				'msg':'Se limpió exitosamente!',
				'vms':vms_json
			})
	


@user_routes.route('/deleteSlice',methods=['GET'])
def deleteSlice():
	idSlice=request.args.get("idSlice")
	slice=SliceBDService.getSliceByID(idSlice)
	if(slice is None):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':'Ups! Ocurrió un error'
		})
	elif (slice.id_vlan is None):
		return jsonify({
			'result':MensajeResultados.failed,
			'msg':'No existe el slice!'
		})
	else:
		vms=VirtualMachineBDService.getVMBySlice(idSlice)
		if vms is None:
			return jsonify({
				'result':MensajeResultados.failed,
				'msg':'Ups! Ocurrió un error'
			})
		else:
			for vm in vms:
				cleanWorker(host=vm.zonaID,id_vlan=idSlice)
				kill_ssh_tunnel_processes(vnc_port=vm.portVNC)
			limpiarDHCP_Interfaces(id_vlan=idSlice)
			VirtualMachineBDService.deleteVMByIdSlice(id_vlan=idSlice)
			SliceBDService.deleteSlice(id_vlan=idSlice)
			SubredesBDService.setActiveOrDesactivSubred(id_Subred=slice.subred,activo=0)
			return jsonify({
				'result':MensajeResultados.success,
				'msg':'Se eliminó el slice exitosamente!',
			})



@user_routes.route('/setNewSlice',methods=['POST'])
def setNewSlice():
	id_vlan = request.form.get('id_vlan', None)
	nombre = request.form.get('nombre')
	vms_data = json.loads(request.form.get('vms'))  
	vms = [VirtualMachineEntity(**vm) for vm in vms_data]
	nombre_dhcp = request.form.get('nombre_dhcp', None)
	topologia_data = json.loads(request.form.get('topologia'))
	topologia = TopologiaEntity(**topologia_data)
	infraestructura = request.form.get('infraestructura', None)
	fecha_creacion = request.form.get('fecha_creacion', None)
	usuario_id = request.form.get('usuario_id')
	subred = request.form.get('subred', None)

	slice_entity = SliceEntity(
		id_vlan=id_vlan,
		nombre=nombre,
		vms=vms,
		nombre_dhcp=nombre_dhcp,
		topologia=topologia,
		infraestructura=infraestructura,
		fecha_creacion=fecha_creacion,
		usuario_id=usuario_id,
		subred=subred
	)

	new_id_vlan=generateNewIDVLan()
	name_dhcp=f"ns-dhcp-{new_id_vlan}"
	id_subred,subred=SubredesBDService.getRandomSubredDesactivado() #Hay que activar la subred
	zonas=ZonaBDService.getAllZonas()
	####### PROBANDO  #########
	for vm in slice_entity.vms:
		vm.imagen['id']
		vm.imagen['path']

	result=SliceBDService.setNewSlice(new_id_vlan=new_id_vlan,cnt_nodos= len(slice_entity.vms),nombre_dhcp= name_dhcp,id_topologia=slice_entity.topologia.id,id_infraestructura=InfraestructuraGlobal.linux ,id_usuario=slice_entity.usuario_id,id_subred= id_subred,nombre=slice_entity.nombre )
	if result:
		init_DHCP(vlan_id=new_id_vlan,dir_net=subred)
		ports=[]
		ips_host=[]
		#2 VMs hasta 5 VMs
		starting_port=5901
		for vm in slice_entity.vms:
			ubicacion=random.randint(0, len(zonas)-1)
			port_vnc=find_available_portVNC(starting_port)			
			mac_addr=generar_mac()
			output=init_VM(vlan_id=new_id_vlan,size_ram=vm.sizeRam,id_worker=ubicacion,path=vm.imagen['path'],mac_addr=mac_addr)			
			stdout_value = output['stdout'].strip()  # Elimina el carácter de nueva línea
			port_vnc_worker = int(stdout_value)

			subprocess.Popen(f"ssh -f -N -L {port_vnc+5900}:localhost:{port_vnc_worker+5900} ubuntu@{zonas[ubicacion].dir_ip}&",shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

			ports.append(port_vnc+5900)
			ips_host.append(zonas[ubicacion].dir_ip)
			starting_port=port_vnc+5900+1
			VirtualMachineBDService.setNewVM(nombre=vm.nombre,vlan_id=new_id_vlan,size_ram=vm.sizeRam,dir_mac=mac_addr,port_vnc=port_vnc+5900,zona_id=zonas[ubicacion].id,image_id=vm.imagen['id'])

		SubredesBDService.setActiveOrDesactivSubred(id_Subred=id_subred,activo=1)

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
