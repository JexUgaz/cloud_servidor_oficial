from email.mime.text import MIMEText
import smtplib
import subprocess
import secrets
import string
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
		caracteres = string.ascii_letters + string.digits + string.punctuation
		contrasena = ''.join(secrets.choice(caracteres) for _ in range(length))
		if(not UserBDService.existeContrasena(contrasena)):
			return contrasena

def	sendMail(msg,receptor,subject):
	conn=smtplib.SMTP(host= 'smtp.gmail.com',port=587)
	conn.ehlo()
	conn.starttls()
	conn.login(user=EmailParams.emisor,password=EmailParams.passApp)
	mensaje=MIMEText(msg,'html')
	mensaje['FROM']=EmailParams.emisor
	mensaje['To']=receptor
	#mensaje['Cc'] = cc
	mensaje['Subject']=subject
	conn.sendmail(from_addr=EmailParams.emisor,to_addrs=receptor,msg=msg.as_string())
	conn.quit()
	print('Email enviado correctamente al destinatario!!')