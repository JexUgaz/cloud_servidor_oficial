from entities.TopologiaEntity import TopologiaEntity
from services.mysql_connect import MySQLConnect

class TopologiaBDService:
    @staticmethod
    def getAllTopologias():
        connection=MySQLConnect.getConnection()
        cursor=connection.cursor(dictionary=True,buffered=False)
        try:
            query = "SELECT * FROM topologias;"
            cursor.execute(query)
            topologia_data = cursor.fetchall()

            topologias = [
                TopologiaEntity(id=topologia[0], nombre=topologia[1])
                for topologia in topologia_data
            ]
            topologias_serializable = [topologia.to_dict() for topologia in topologias]

            return topologias_serializable
            
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
    