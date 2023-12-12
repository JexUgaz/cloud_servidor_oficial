import argparse
import subprocess

def runCommand(command):
    result=subprocess.run("sudo "+command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return result.stdout.strip()

def eliminarDHCP(id_vlan):
    print(f"sudo ip netns delete ns-dhcp-{id_vlan}")
    #runCommand(f"ip netns delete ns-dhcp-{id_vlan}")

def kill_dnsmasq_processes(id_vlan):
    pid = runCommand(f"ps -aux | grep dnsmasq | grep tap{id_vlan}-dhcp | grep -v grep | awk '{{print $2}}'")
    print(f"kill -9 {pid}")
    #runCommand(f"kill -9 {pid}")

def remove_interfaces_with_idVlan(idVlan):
    result = runCommand(f"ovs-vsctl show | awk '/{idVlan}/ && /Interface/ {{print $2}}'")
    interfaces = result.splitlines()

    for interface in interfaces:
        print(f"sudo ovs-vsctl del-port {interface}")
        #runCommand(f"ovs-vsctl del-port {interface}")

def kill_ssh_tunnel_processes(vnc_port):
    pid = runCommand(f"ps -aux | grep ssh | grep {vnc_port}:localhost | grep -v grep | awk '{{print $2}}'")
    print(f"sudo kill -9 {pid}")
    #runCommand(f"kill -9 {pid}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kill QEMU processes associated with a specific VLAN ID.")
    parser.add_argument("id_vlan", type=int, help="VLAN ID for which QEMU processes should be killed.")
    parser.add_argument('vnc_port1', type=str, help='Puerto VNC 1')
    parser.add_argument('vnc_port2', type=str, help='Puerto VNC 2')
    
    args = parser.parse_args()
    id_vlan=args.id_vlan
    vnc_port1=args.vnc_port1
    vnc_port2=args.vnc_port2

    eliminarDHCP(id_vlan)
    remove_interfaces_with_idVlan(id_vlan)
    kill_dnsmasq_processes(id_vlan)
    kill_ssh_tunnel_processes(vnc_port1)
    kill_ssh_tunnel_processes(vnc_port2)
