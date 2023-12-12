from entities.VirtualMachineEntity import VirtualMachineEntity
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

    @staticmethod
    def deleteVMByIdSlice(id_vlan):
        connection=MySQLConnect.getConnection()
        cursor = connection.cursor()
        try:
            query = "delete from vms where slices_id_vlan=%s;"
            values = (id_vlan,)
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
    def existeMac(dir_mac):
        connection=MySQLConnect.getConnection()
        cursor=connection.cursor(dictionary=True,buffered=False)
        try:
            query = "SELECT * FROM vms WHERE dir_mac = %s;"
            cursor.execute(query,(dir_mac,))
            json = cursor.fetchone()
            
            if cursor.rowcount == 0:
                return False

            return True
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
    @staticmethod
    def getVMBySlice(id_vlan):
        connection=MySQLConnect.getConnection()
        cursor=connection.cursor(dictionary=True,buffered=False)
        try:
            query = """
                select v.id,v.nombre,v.size_ram,v.fecha_creacion,v.dir_mac,v.port_vnc,z.dir_ip 'zona' 
                from vms v
                    left join zona z on z.id=v.zona_id
                where v.slices_id_vlan=%s;
            """
            cursor.execute(query, (id_vlan,))
            vms_json = cursor.fetchall()
            print(f"vms_json: {vms_json}")
            vm = [
                VirtualMachineEntity(id=vm['id'],nombre=vm['nombre'],sizeRam=vm['size_ram'],fechaCreacion=vm['fecha_creacion'],dirMac=vm['dir_mac'],portVNC=vm['port_vnc'],zonaID=vm['zona'],imagen=None)
                for vm in vms_json
            ]
            return vm
        except Exception as e:
            print(f"Exception: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()
