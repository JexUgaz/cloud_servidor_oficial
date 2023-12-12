from typing import List
from entities.ZonaEntity import ZonaEntity
from services.mysql_connect import MySQLConnect


class ZonaBDService:
    @staticmethod
    def getAllZonas()->List[ZonaEntity]:
        connection = MySQLConnect.getConnection()
        cursor = connection.cursor(dictionary=True, buffered=False)
        
        try:
            query = "select * from zona;"
            cursor.execute(query)

            result = []
            for row in cursor.fetchall():
                zona = ZonaEntity.convertToZona(json=row)
                result.append(zona.to_dict())
            
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