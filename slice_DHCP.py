import subprocess
import ipaddress as ipaddr
from config.helpers import runCommand

def _getIpCount(ipNetwork,i,mask=True):
	net= ipaddr.IPv4Network(ipNetwork)
	if mask:
		return str(net.network_address+i)+"/"+ipNetwork.split("/")[1]
	else:
		return str(net.network_address+i)

def _getMask(ipNetwork):
	net= ipaddr.IPv4Network(ipNetwork)
	return str(net.netmask)

def _createTap(idVlan,name_OVS):
	runCommand(f"ovs-vsctl add-port {name_OVS} tap{idVlan}-dhcp tag={idVlan} -- set interface tap{idVlan}-dhcp type=internal")
	print(f"TAP 'tap{idVlan}-dhcp' creado exitoso internamente!")


def _createNsDHCP(id):
	runCommand(f"ip netns add ns-dhcp-{id}")
	runCommand(f"ip link set tap{id}-dhcp netns ns-dhcp-{id}") #Añadimos tap a DHCP
	runCommand(f"ip netns exec ns-dhcp-{id} ip link set dev lo up")
	runCommand(f"ip netns exec ns-dhcp-{id} ip link set dev tap{id}-dhcp up") #Levantamos interfaz tap del DHCP
	print(f"DHCP y DNS Server: ns-dhcp-{id} creado exitosamente!")


def _finalConfigs(idVlan,dir_net,name_ovs):
	#Asignamos IP a la interfaz del DHCP conectado al OVS
	ipDHCP=_getIpCount(dir_net,2)
	runCommand(f"ip netns exec ns-dhcp-{idVlan} ip address add {ipDHCP} dev tap{idVlan}-dhcp")
	
	#Interfaz del OVS para salido a internet
	runCommand(f"ovs-vsctl add-port {name_ovs} tap{idVlan}-gateway tag={idVlan} -- set interface tap{idVlan}-gateway type=internal")
	runCommand(f"ip link set dev tap{idVlan}-gateway up")

	ipGateway=_getIpCount(dir_net,1) #Obtenemos el ip Gateway
	runCommand(f"ip address add {ipGateway} dev tap{idVlan}-gateway")

	#Encendemos Servidor DHCP y DNS dentro del namespace
	ipGateway=_getIpCount(dir_net,1,mask=False)
	mask_format=_getMask(dir_net)

	ini_range=_getIpCount(dir_net,3,mask=False)
	fin_range=_getIpCount(dir_net,7,mask=False)
	runCommand(f"ip netns exec ns-dhcp-{idVlan} dnsmasq --interface=tap{idVlan}-dhcp --dhcp-range={ini_range},{fin_range},{mask_format} --dhcp-option=3,{ipGateway} --dhcp-option=6,8.8.8.8 --dhcp-option=6,8.8.4.4")
	print("------->    Server DHCP y DNS encendidos y conectados al Switch OVS!!    <--------")


def init_DHCP(vlan_id,dir_net,name_OVS="br-vlan"):
	_createTap(vlan_id,name_OVS) #Creamos las interfaces con vlan
	_createNsDHCP(vlan_id) #Creamos el Namespaces DHCP-DNS Server y unimos las interfaces vlan
	_finalConfigs(vlan_id,dir_net,name_OVS) #Levantamientos y configuraciones IP
	print("\n")