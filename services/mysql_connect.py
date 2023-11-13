import mysql.connector

class MySQLConnect:
    db_connection = None

    @staticmethod
    def initialConnection():
        db_config = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': 'cloudpass',
            'database': 'bd_cloud',
            'port': 3400,
        }
        MySQLConnect.db_connection = mysql.connector.connect(**db_config)
        
    
