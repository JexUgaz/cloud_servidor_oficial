import subprocess
import paramiko
import argparse

#Datos de conexión SSH
hosts = ['10.0.0.30','10.0.0.40','10.0.0.50']
port = 22  # Puerto SSH, generalmente 22
username = 'ubuntu'
password = 'ubuntu'

def runCommandSSH(command, ssh):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()

    output = {
        'stdout': stdout.read().decode('utf-8'),
        'stderr': stderr.read().decode('utf-8'),
        'exit_code': exit_code
    }

    return output

def init_VM(vlan_id,size_ram,id_worker,path,mac_addr,name_ovs='br-vlan'):
	#name_vm=slice50-vmX
	ssh = paramiko.SSHClient()

	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	ssh.connect(hosts[int(id_worker)], port, username, password, look_for_keys=False)
	output=runCommandSSH(f'sudo python3 proyecto/createVM.py {name_ovs} {vlan_id} {path} {size_ram} {mac_addr}',ssh)
	ssh.close()
	return output
      
	 
