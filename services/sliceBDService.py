from typing import List
from config.globals import HelperGlobal
from entities.SliceEntity import SliceEntity
from services.mysql_connect import MySQLConnect

class SliceBDService:
    @staticmethod
    def getSliceByID(id_vlan):
        connection=MySQLConnect.getConnection()
        cursor=connection.cursor(dictionary=True,buffered=False)
        try:
            query = "select * from slices where id_vlan=%s;"
            cursor.execute(query, (id_vlan,))
            json = cursor.fetchone()
            
            if cursor.rowcount == 0:
                return SliceEntity(
                    id_vlan=None,
                    nombre=None,
                    vms=None,
                    nombre_dhcp=None,
                    topologia=None,
                    infraestructura=None,
                    fecha_creacion=None,
                    usuario_id=None,
                    subred=None
                )

            slice=SliceEntity.convert_to_slice_entity(data=json,topologia=None,vms=None)
            return slice
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
    
    @staticmethod
    def setNewSlice(new_id_vlan,cnt_nodos,nombre_dhcp,id_topologia,id_infraestructura,id_usuario,id_subred,nombre):
        connection=MySQLConnect.getConnection()
        cursor = connection.cursor()
        try:            
            # Llamar al procedimiento almacenado
            values = (new_id_vlan,cnt_nodos,nombre_dhcp,id_topologia,id_infraestructura,id_usuario,id_subred,nombre)
            # Recuperar el resultado del procedimiento
            cursor.execute(""" insert into slices 
                (id_vlan,cantidad_nodos,nombre_dhcp,topologias_id,infraestructura_id,fecha_creacion,usuario_id,subredes_id,nombre)
                values (%s,%s,%s,%s,%s,current_time(),%s,%s,%s);   """,values)
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
    def getAllSlices() -> List[SliceEntity]:
        connection = MySQLConnect.getConnection()
        cursor = connection.cursor()

        try:
            query = """
                select s.id_vlan,s.nombre,s.fecha_creacion,u.nombre 'creador',t.nombre 'topologia',s.cantidad_nodos 'n_nodos',su.dir_red from slices s
                    left join usuario u on u.id=s.usuario_id
                    left join topologias t on t.id=s.topologias_id
                    left join subredes su on su.id=s.subredes_id;
            """
            cursor.execute(query)
            slice_data = cursor.fetchall()

            slices = [
                {
                    'id_vlan': slice[0],
                    'nombre': slice[1],
                    'fecha_creacion':HelperGlobal.getStringFechaFormat(slice[2]),
                    'creador':slice[3],
                    'topologia': slice[4],
                    'n_nodos': slice[5],
                    'dir_red': slice[6]
                }
                for slice in slice_data
            ]
            return slices
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
    @staticmethod
    def getSlicesByUser(usuario_id) -> List[SliceEntity]:
        connection = MySQLConnect.getConnection()
        cursor = connection.cursor()

        try:
            query = """
                select s.id_vlan,s.nombre,s.fecha_creacion,u.nombre 'creador',t.nombre 'topologia',s.cantidad_nodos 'n_nodos',su.dir_red from slices s
                    left join usuario u on u.id=s.usuario_id
                    left join topologias t on t.id=s.topologias_id
                    left join subredes su on su.id=s.subredes_id
                where s.usuario_id=%s;
            """
            cursor.execute(query,(usuario_id,))
            slice_data = cursor.fetchall()

            slices = [
                {
                    'id_vlan': slice[0],
                    'nombre': slice[1],
                    'fecha_creacion':HelperGlobal.getStringFechaFormat(slice[2]),
                    'creador':slice[3],
                    'topologia': slice[4],
                    'n_nodos': slice[5],
                    'dir_red': slice[6]
                }
                for slice in slice_data
            ]
            return slices
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
