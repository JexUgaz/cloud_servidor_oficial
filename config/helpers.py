from email.mime.text import MIMEText
import random
import smtplib
import socket
import subprocess
from config.globals import EmailParams
from services.sliceBDService import SliceBDService
from services.userBDService import UserBDService

class MensajeResultados:
	success="success"
	failed="failed"

def runCommand(command):
	result=subprocess.run("sudo "+command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	return result.stdout.strip()

def getIDOpenstackUserByName(name):
	return runCommand(f"sh -c '. ~/env-scripts/admin-openrc;openstack user list' | grep '{name}'"+" | awk '{print $2}'")

def generateNewPass():
	while True:
		length=10
		contrasena=runCommand(f"openssl rand -base64 {length}")
		if(not UserBDService.existeContrasena(contrasena)):
			return contrasena
def generateNewIDVLan():
    while True:
        length=7
        digitos = [str(random.randint(0, 9)) for _ in range(length)]
        # Concatena los dígitos para formar el número completo
        new_id = ''.join(digitos)
        slice=SliceBDService.getSliceByID(new_id)
        if(slice is None or slice.id_vlan is None):
        	return new_id

def sendMail(msg, receptor, subject):
    conn = smtplib.SMTP(host='smtp.gmail.com', port=587)
    conn.ehlo()
    conn.starttls()
    conn.login(user=EmailParams.emisor, password=EmailParams.passApp)

    mensaje = MIMEText(msg, 'html', 'utf-8')  # Indicar el charset como 'utf-8'
    mensaje['FROM'] = EmailParams.emisor
    mensaje['To'] = receptor
    mensaje['Subject'] = subject

    # Convertir el mensaje a una cadena utf-8 antes de enviarlo
    conn.sendmail(from_addr=EmailParams.emisor, to_addrs=receptor, msg=mensaje.as_string().encode('utf-8'))
    conn.quit()

    print('Email enviado correctamente al destinatario!!')

def find_available_portVNC(starting_port=5901):
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', starting_port))
                return starting_port-5900
        except socket.error:
            starting_port += 1

def generar_mac():
	parte_fija = "fa:16:3e"
	resto = ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(3)])
	direccion_mac = parte_fija + ':' + resto
	return direccion_mac