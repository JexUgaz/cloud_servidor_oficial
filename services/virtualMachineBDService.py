from services.mysql_connect import MySQLConnect


class VirtualMachineBDService:
    @staticmethod
    def setNewVM(nombre,vlan_id,size_ram,dir_mac,port_vnc,zona_id,image_id):
        connection=MySQLConnect.getConnection()
        cursor = connection.cursor()
        try:
            query = """
                insert into vms (nombre,slices_id_vlan,size_ram,fecha_creacion,dir_mac,port_vnc,zona_id,imagenes_id)
                values (%s,%s,%s,current_timestamp(),%s,%s,%s,%s);
            """
            values = (nombre,vlan_id,size_ram,dir_mac,port_vnc,zona_id,image_id)
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