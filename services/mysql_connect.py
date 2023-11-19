import platform
import mysql.connector

class MySQLConnect:
    db_connection = None

    @staticmethod
    def initialConnection():
        sys_op= platform.system()
        if sys_op=="Linux":
            hostMySQL= '127.0.0.1'
        elif sys_op=="Windows":
            hostMySQL= '10.20.10.113'
        db_config = {
            'host': hostMySQL,
            'user': 'root',
            'password': 'cloudpass',
            'database': 'bd_cloud',
            'port': 3400,
        }
        MySQLConnect.db_connection = mysql.connector.connect(**db_config)
        
    
