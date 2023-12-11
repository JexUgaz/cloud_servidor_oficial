import subprocess
import paramiko
import argparse

#Datos de conexión SSH
hosts = ['10.0.0.30','10.0.0.40','10.0.0.50']
port = 22  # Puerto SSH, generalmente 22
username = 'ubuntu'
password = 'ubuntu'

def runCommandSSH(command,ssh):
	stdin, stdout, stderr = ssh.exec_command(command)

def init_VM(vlan_id,port_vnc,size_ram,id_worker,path,mac_addr,name_ovs='br-vlan'):
	#name_vm=slice50-vmX
	ssh = paramiko.SSHClient()

	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	ssh.connect(hosts[int(id_worker)], port, username, password)
	print(f'sudo python3 proyecto/createVM.py {name_ovs} {vlan_id} {port_vnc} {path} {size_ram} {mac_addr}')
	runCommandSSH(f'sudo python3 proyecto/createVM.py {name_ovs} {vlan_id} {port_vnc} {path} {size_ram} {mac_addr}',ssh)
	ssh.close()
