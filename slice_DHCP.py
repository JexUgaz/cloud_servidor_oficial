import subprocess
import ipaddress as ipaddr
import argparse

def getIpCount(ipNetwork,i,mask=True):
	net= ipaddr.IPv4Network(ipNetwork)
	if mask:
		return str(net.network_address+i)+"/"+ipNetwork.split("/")[1]
	else:
		return str(net.network_address+i)

def getMask(ipNetwork):
	net= ipaddr.IPv4Network(ipNetwork)
	return str(net.netmask)

def runCommand(command):
	print(command)
	result=subprocess.run(command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

def createTap(idVlan,name_OVS):
	runCommand(f"ovs-vsctl add-port {name_OVS} tap{idVlan}-dhcp tag={idVlan} -- set interface tap{idVlan}-dhcp type=internal")
	print(f"TAP 'tap{idVlan}-dhcp' creado exitoso internamente!")


def createNsDHCP(id):
	runCommand(f"ip netns add ns-dhcp-{id}")
	runCommand(f"ip link set tap{id}-dhcp netns ns-dhcp-{id}") #Añadimos tap a DHCP
	runCommand(f"ip netns exec ns-dhcp-{id} ip link set dev lo up")
	runCommand(f"ip netns exec ns-dhcp-{id} ip link set dev tap{id}-dhcp up") #Levantamos interfaz tap del DHCP
	print(f"DHCP y DNS Server: ns-dhcp-{id} creado exitosamente!")


def finalConfigs(idVlan,dir_net,ini_range,fin_range,name_ovs):
	#Asignamos IP a la interfaz del DHCP conectado al OVS
	ipDHCP=getIpCount(dir_net,2)
	runCommand(f"ip netns exec ns-dhcp-{idVlan} ip address add {ipDHCP} dev tap{idVlan}-dhcp")
	
	#Interfaz del OVS para salido a internet
	runCommand(f"ovs-vsctl add-port {name_ovs} tap{idVlan}-gateway tag={idVlan} -- set interface tap{idVlan}-gateway type=internal")
	runCommand(f"ip link set dev tap{idVlan}-gateway up ")

	ipGateway=getIpCount(dir_net,1) #Obtenemos el ip Gateway
	runCommand(f"ip address add {ipGateway} dev tap{idVlan}-gateway")

	#Encendemos Servidor DHCP y DNS dentro del namespace
	ipGateway=getIpCount(dir_net,1,mask=False)
	mask_format=getMask(dir_net)
	runCommand(f"ip netns exec ns-dhcp-{idVlan} dnsmasq --interface=tap{idVlan}-dhcp --dhcp-range={ini_range},{fin_range},{mask_format} --dhcp-option=3,{ipGateway} --dhcp-option=6,8.8.8.8 --dhcp-option=6,8.8.4.4")
	print("------->    Server DHCP y DNS encendidos y conectados al Switch OVS!!    <--------")

def init():
	parser = argparse.ArgumentParser(description='Argumentos de entrada')

	parser.add_argument('param1', type=str, help='Nombre del OVS')
	parser.add_argument('param2', type=str, help='ID de la Vlan')
	parser.add_argument('param3', type=str, help='Dirección de red')
	parser.add_argument('param4', type=str, help='Inicial DHCP')
	parser.add_argument('param5', type=str, help='Fin DHCP')

	args = parser.parse_args()

	ame_vm=args.param1

	name_OVS = args.param1
	vlan_id = args.param2 #N° Entero, ID del slice en la BD
	dir_net = args.param3
	ini_dhcp= args.param4
	fin_dhcp= args.param5
	
	createTap(vlan_id,name_OVS) #Creamos las interfaces con vlan
	
	createNsDHCP(vlan_id) #Creamos el Namespaces DHCP-DNS Server y unimos las interfaces vlan
	
	finalConfigs(vlan_id,dir_net,ini_dhcp,fin_dhcp,name_OVS) #Levantamientos y configuraciones IP

	print("\n")

if __name__=='__main__':
	init()
