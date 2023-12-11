import json
from typing import List
from entities.TopologiaEntity import TopologiaEntity
from entities.VirtualMachineEntity import VirtualMachineEntity

class SliceEntity:
    def __init__(self, nombre,id_vlan, vms:List[VirtualMachineEntity], nombre_dhcp, topologia:TopologiaEntity, infraestructura, fecha_creacion, usuario_id, subred):
        self.id_vlan = id_vlan
        self.nombre=nombre
        self.vms = vms
        self.nombre_dhcp = nombre_dhcp
        self.topologia = topologia
        self.infraestructura = infraestructura
        self.fecha_creacion = fecha_creacion
        self.usuario_id = usuario_id
        self.subred = subred

    @staticmethod
    def convert_to_slice_entity(data,vms,topologia):
        return SliceEntity(
            nombre=data.get('nombre'),
            id_vlan=data.get('id_vlan'),
            vms=vms,
            nombre_dhcp=data.get('nombre_dhcp'),
            topologia=topologia,
            infraestructura=data.get('infraestructura'),
            fecha_creacion=data.get('fecha_creacion'),
            usuario_id=data.get('usuario_id'),
            subred=data.get('subred')
        )


    def __str__(self):
        return f"Slice(id_vlan={self.id_vlan}, vms={self.vms}, nombre_dhcp='{self.nombre_dhcp}', topologia={self.topologia}, infraestructura={self.infraestructura}, fecha_creacion='{self.fecha_creacion}', usuario_id={self.usuario_id}, subred={self.subred})"
