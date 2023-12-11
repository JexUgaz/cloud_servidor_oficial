from services.mysql_connect import MySQLConnect

class SubredesBDService:
    @staticmethod
    def setNewSubredes(indice_subred):
        connection=MySQLConnect.getConnection()
        cursor = connection.cursor()
        try:
            query = "call InsertarDirecciones(%s);"
            values = (indice_subred,)
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
    def getLastDirSubred():
        connection=MySQLConnect.getConnection()
        cursor=connection.cursor(dictionary=True,buffered=False)
        try:
            query = "SELECT dir_red FROM subredes ORDER BY id DESC LIMIT 1;"
            cursor.execute(query)
            json = cursor.fetchone()
            
            if cursor.rowcount == 0:
                return None

            return json["dir_red"]
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
    
    @staticmethod
    def getAllSubredes():
        connection=MySQLConnect.getConnection()
        cursor=connection.cursor(dictionary=True,buffered=False)
        try:
            query = "SELECT * FROM subredes;"
            cursor.execute(query)
            
            result = []
            for row in cursor.fetchall():
                result.append([row["id"],row["dir_red"],row["activo"]])

            if cursor.rowcount == 0:
                return []
            
            return result
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
    