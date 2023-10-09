import subprocess
import paramiko

#Datos de conexión SSH
hosts = ['10.0.0.30','10.0.0.40','10.0.0.50']
port = 22  # Puerto SSH, generalmente 22
username = 'ubuntu'
password = 'ubuntu'


def runCommand(command):
        result=subprocess.run(command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        print(result.stdout)
        return result.stdout

def runCommandSSH(command,ssh):
	stdin, stdout, stderr = ssh.exec_command(command)

	# Leer la salida del comando
	output = stdout.read().decode('utf-8')

	# Imprimir la salida
	#print("Salida del comando: "+output)

def test(ssh,interface,name_ovs):
	runCommandSSH(f'sudo python3 cloud_lab4/initWorker.py {name_ovs} {interface}',ssh)

if __name__=='__main__':
	name_ovs= input('Ingrese el nombre del OVS (br-int): ')
	intWorker= input('Ingrese la interfaz de los workers (ens4): ')
	for host in hosts:

		ssh = paramiko.SSHClient()

		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		ssh.connect(host, port, username, password)

		test(ssh,intWorker,name_ovs)

		ssh.close()
