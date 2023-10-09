from flask import Flask,jsonify,request
import subprocess

app= Flask(__name__)

def runCommand(command):
	result=subprocess.run("sudo "+command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	#print(command)


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
		'msg':'Creado exitosamente!'
	})

if __name__=="__main__":
	app.run(debug=True,port=5001)
