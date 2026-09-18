from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id, usuario, password):
        self.id = id
        self.usuario = usuario
        self.password = password