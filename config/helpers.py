import subprocess

class MensajeResultados:
	success="success"
	failed="failed"

def runCommand(command):
	result=subprocess.run("sudo "+command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	return result.stdout.strip()

def getIDUserByName(name):
	return runCommand(f"sh -c '. ~/env-scripts/admin-openrc;openstack user list' | grep '{name}'"+" | awk '{print $2}'")
