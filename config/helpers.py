from email.mime.text import MIMEText
import smtplib
import subprocess
from config.globals import EmailParams
from services.userBDService import UserBDService

class MensajeResultados:
	success="success"
	failed="failed"

def runCommand(command):
	result=subprocess.run("sudo "+command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	return result.stdout.strip()

def getIDUserByName(name):
	return runCommand(f"sh -c '. ~/env-scripts/admin-openrc;openstack user list' | grep '{name}'"+" | awk '{print $2}'")

def generateNewPass():
	while True:
		length=10
		contrasena=runCommand(f"openssl rand -base64 {length}")
		if(not UserBDService.existeContrasena(contrasena)):
			return contrasena

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
