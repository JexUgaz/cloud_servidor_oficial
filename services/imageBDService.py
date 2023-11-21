from services.mysql_connect import MySQLConnect

class ImageBDService:
    @staticmethod
    def setNewImage(path,nombre,usuario_id):
        connection=MySQLConnect.getConnection()
        cursor = connection.cursor()
        try:
            query = "INSERT INTO imagenes (path, nombre, usuario_id) VALUES (%s,%s,%s);"
            values = (path,nombre,usuario_id)
            cursor.execute(query, values)
            connection.commit()
            return True
        except Exception as e:
            print(f"Exception: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()