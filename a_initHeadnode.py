import subprocess

def runCommand(command):
	result=subprocess.run(command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	#print(result.stdout)
	return result.stdout

def createOVS(name_ovs):
	runCommand(f"ovs-vsctl add-br {name_ovs}")
	runCommand("ovs-vsctl list-br")

def addPortInOVS(intX,name_ovs):
	runCommand(f"ovs-vsctl add-port {name_ovs} {intX}")
	runCommand(f"ip link set dev {intX} up")
	runCommand(f"ovs-vsctl list-ports {name_ovs}")

def actIpv4Forward():
	runCommand("sysctl net.ipv4.ip_forward") #Ya está activo, falta activarlo si es que no estuviera activo

def changeForwardToDrop():
	runCommand("iptables -P FORWARD DROP")
	print("DROP el Forward")

if __name__=='__main__':
	name_ovs=input("Ingrese el nombre de la ovs: ")
	createOVS(name_ovs)
	int1=input("Ingrese el nombre de la interfaz 'ens5': ")
	addPortInOVS(int1,name_ovs)
	
	actIpv4Forward()

	changeForwardToDrop()
