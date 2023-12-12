from datetime import datetime as dt


class RolesGlobal:
    usuario=2
    administrador=1

class EmailParams:
	passApp='leowrijstdhtwnau'
	emisor='loammi.jezreel@gmail.com'

class InfraestructuraGlobal:
    openstack=1
    linux=2
class HelperGlobal:
    def getStringFechaFormat(fecha):
        return fecha.strftime("%d/%m/%Y %H:%M:%S")
