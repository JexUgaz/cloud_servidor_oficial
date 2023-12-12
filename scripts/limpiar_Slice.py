import argparse
import subprocess

import paramiko

from createVM import runCommandSSH

def runCommand(command):
    result=subprocess.run("sudo "+command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return result.stdout.strip()

def _eliminarDHCP(id_vlan):
    runCommand(f"ip netns delete ns-dhcp-{id_vlan}")

def _kill_dnsmasq_processes(id_vlan):
    pid = runCommand(f"ps -aux | grep dnsmasq | grep tap{id_vlan}-dhcp | grep -v grep | awk '{{print $2}}'")
    runCommand(f"kill -9 {pid}")

def _remove_interfaces_with_idVlan(idVlan):
    result = runCommand(f"ovs-vsctl show | awk '/{idVlan}/ && /Interface/ {{print $2}}'")
    interfaces = result.splitlines()

    for interface in interfaces:
        runCommand(f"ovs-vsctl del-port {interface}")

def kill_ssh_tunnel_processes(vnc_port):
    pid = runCommand(f"ps -aux | grep ssh | grep {vnc_port}:localhost | grep -v grep | awk '{{print $2}}'")
    runCommand(f"kill -9 {pid}")

def cleanWorker(host,id_vlan):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, 22, 'ubuntu', 'ubuntu', look_for_keys=False)
    output=runCommandSSH(f'sudo python3 proyecto/removeVMs.py {id_vlan}',ssh)
    ssh.close()

def limpiarDHCP_Interfaces(id_vlan):
    _eliminarDHCP(id_vlan)
    _remove_interfaces_with_idVlan(id_vlan)
    _kill_dnsmasq_processes(id_vlan)

    
