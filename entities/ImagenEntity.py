class ImagenEntity:
    def __init__(self, path, nombre, usuario_id, id):
        self.path = path
        self.nombre = nombre
        self.usuario_id = usuario_id
        self.id = id
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'nombre': self.nombre,
            'path': self.path
        }

    @staticmethod
    def convertToImagen(json):
        return ImagenEntity(
            id=json['id'],
            nombre=json['nombre'],
            path=json['path'],
            usuario_id=json['usuario_id']
        )
    
    def __str__(self):
        return f"Imagen(id={self.id}, path={self.path}, nombre={self.nombre}, usuario_id={self.usuario_id})"
