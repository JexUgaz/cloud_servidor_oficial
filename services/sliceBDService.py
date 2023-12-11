from services.mysql_connect import MySQLConnect

class SliceBDService:
    @staticmethod
    def setNewSlice(cnt_nodos,nombre_dhcp,id_topologia,id_infraestructura,id_usuario,id_subred,nombre):
        connection=MySQLConnect.getConnection()
        cursor = connection.cursor()
        try:
            query = """
                insert into slices 
                (cantidad_nodos,nombre_dhcp,topologias_id,infraestructura_id,fecha_creacion,usuario_id,subredes_id,nombre)
                values (%s,%s,%s,%s,current_time(),%s,%s,%s);   

                SELECT LAST_INSERT_ID() AS nuevo_id;         
            """
            values = (cnt_nodos,nombre_dhcp,id_topologia,id_infraestructura,id_usuario,id_subred,nombre)
            cursor.execute(query, values)
            result =cursor.fetchall()
            nuevo_id = result[0][0] if result else None

            connection.commit()
        
            return nuevo_id
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()