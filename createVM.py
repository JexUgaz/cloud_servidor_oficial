import subprocess
import paramiko
import argparse

#Datos de conexión SSH
hosts = ['10.0.0.30','10.0.0.40','10.0.0.50']
port = 22  # Puerto SSH, generalmente 22
username = 'ubuntu'
password = 'ubuntu'


def runCommand(command):
	result=subprocess.run(command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	#print(result.stdout)

def runCommandSSH(command,ssh):
	#print(f"SSH: {command}")
	stdin, stdout, stderr = ssh.exec_command(command)

def send(ssh,name_vm,name_ovs,vlan_id,port_vnc):
	runCommandSSH(f'sudo python3 proyecto/createVM.py {name_vm} {name_ovs} {vlan_id} {port_vnc}',ssh)


if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Argumentos de entrada')
        
	parser.add_argument('param1', type=str, help='Nombre de la Vm')
	parser.add_argument('param2', type=str, help='ID de la Vlan')
	parser.add_argument('param3', type=str, help='Puerto VNC')
	parser.add_argument('param4', type=str, help='Size RAM de VM')
	parser.add_argument('param5', type=str, help='ID del Worker 0,1,2')

	args = parser.parse_args()

	name_ovs='br-int'
	name_vm=args.param1 #slice50-vmX
	vlan_id= args.param2 #50 por ahora
	port_vnc= args.param3 
	size_ram=args.param4
	id_worker=args.param5

	ssh = paramiko.SSHClient()

	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	ssh.connect(hosts[int(id_worker)], port, username, password)

	send(ssh,name_vm,name_ovs,vlan_id,port_vnc)

	ssh.close()
