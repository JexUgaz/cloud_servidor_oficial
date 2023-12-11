class TopologiaEntity:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
        }

    def __str__(self):
        return f"Topologia(id={self.id}, nombre='{self.nombre}')"