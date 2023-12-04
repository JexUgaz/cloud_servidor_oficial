class UsuarioEntity:
    def __init__(self, id, nombre, email, roles_id):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.roles_id = roles_id

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'roles_id': self.roles_id
        }

    def __str__(self):
        return f"Usuario(id={self.id}, nombre={self.nombre}, email={self.email}, roles_id={self.roles_id})"