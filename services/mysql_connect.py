from flask_mysqldb import MySQL

class MySQLConnect:
    mysql = None

    @staticmethod
    def initialConnection(app):
        # Configuración de la base de datos
        app.config['MYSQL_HOST'] = 'localhost'  # Cambia a la IP de tu máquina si MySQL está en otro host
        app.config['MYSQL_PORT'] = 3400  # Cambia al puerto correcto
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = 'cloudpass'
        app.config['MYSQL_DB'] = 'bd_cloud'

        # Inicialización de la extensión MySQL
        MySQLConnect.mysql = MySQL(app)
    