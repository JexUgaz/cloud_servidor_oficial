class ZonaEntity:
    def __init__(self, id,nombre,dir_ip):
        self.id=id
        self.nombre = nombre
        self.dir_ip=dir_ip

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'dir_ip': self.dir_ip
        }

    @staticmethod
    def convertToZona(json):
        return ZonaEntity(
            id=json['id'],
            nombre=json['nombre'],
            dir_ip=json['dir_ip']
        )
    
    def __str__(self):
        return f"ZonaEntity(id={self.id}, nombre={self.nombre}, dir_ip={self.dir_ip})"
