from entities.ImagenEntity import ImagenEntity
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
                
    @staticmethod
    def deleteImage(idImage):
        connection=MySQLConnect.getConnection()
        cursor = connection.cursor()
        try:
            query = "DELETE FROM imagenes WHERE id=%s;"
            values = (idImage,)
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
    def getImageById(idImage):
        connection=MySQLConnect.getConnection()
        cursor=connection.cursor(dictionary=True,buffered=False)
        try:
            query = "select * from imagenes where id=%s"
            cursor.execute(query, (idImage,))
            json = cursor.fetchone()
            
            if cursor.rowcount == 0:
                return ImagenEntity(id=None,nombre=None,email=None,roles_id=None)

            image=ImagenEntity.convertToImagen(json=json)
            return image
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
    
    @staticmethod
    def getAllImages():
        connection = MySQLConnect.getConnection()
        cursor = connection.cursor(dictionary=True, buffered=False)
        
        try:
            query = """select i.id,i.path,i.nombre,u.nombre as 'usuario_id' from imagenes i
	                    left join usuario u on (u.id=i.usuario_id);"""
            cursor.execute(query)

            result = []
            for row in cursor.fetchall():
                imagen = ImagenEntity.convertToImagen(json=row)
                result.append(imagen.to_dict())
            
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
    
    @staticmethod
    def getImagesByUser(idUser):
        connection = MySQLConnect.getConnection()
        cursor = connection.cursor(dictionary=True, buffered=False)
        
        try:
            query = "select * from imagenes where usuario_id=%s"
            cursor.execute(query, (idUser,))

            result = []
            for row in cursor.fetchall():
                imagen = ImagenEntity.convertToImagen(json=row)
                result.append(imagen.to_dict())
            
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
