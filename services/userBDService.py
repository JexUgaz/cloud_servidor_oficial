from services.mysql_connect import MySQLConnect

class UserBDService():
    @staticmethod
    def getUserByCredentials(name,password):
        connection=MySQLConnect.getConnection()
        cursor=connection.cursor(dictionary=True,buffered=False)
        try:
            query = "select * from bd_cloud.usuario where nombre=%s and password=SHA2(%s,256)"
            cursor.execute(query, (name, password))
            user = cursor.fetchone()
            return user
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

    @staticmethod
    def setNewUser(name,password,email,rol,id):
        connection=MySQLConnect.getConnection()
        cursor = connection.cursor()
        try:
            query = "INSERT INTO usuario (id,nombre, password, email, roles_id) VALUES (%s,%s, SHA2(%s, 256), %s, %s);"
            values = (id,name, password, email, rol)
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

    @staticmethod
    def deleteUserByID(id):
        connection=MySQLConnect.getConnection()
        cursor = connection.cursor()
        try:
            query = "DELETE FROM usuario WHERE id = %s"
            cursor.execute(query, (id,))
            connection.commit()
            return True
        except Exception as e:
            return False
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

