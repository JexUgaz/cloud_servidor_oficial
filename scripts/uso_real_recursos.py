import time
import paramiko
from prettytable import PrettyTable
import csv
from datetime import datetime
def obtener_tiempos_idle_desde_csv_Real(csv_path):
    tiempos_idle = []

    try:
        with open(csv_path, mode='r') as archivo_csv:
            csv_reader = csv.reader(archivo_csv)
            next(csv_reader)  # Saltar la fila de encabezado
            for row in csv_reader:
                _, idle_str = row  # Solo necesitas la segunda columna
                tiempo_idle = int(idle_str)
                tiempos_idle.append(tiempo_idle)

        # Tomar los dos últimos valores si hay más de dos
        tiempos_idle = tiempos_idle[-2:]

        return tiempos_idle

    except Exception as e:
        print(f"Error al obtener los tiempos idle desde el archivo CSV: {e}")
        return None
def obtener_tiempos_idle_desde_csv(csv_path):
    tiempos_idle = []

    try:
        with open(csv_path, mode='r') as archivo_csv:
            csv_reader = csv.reader(archivo_csv)
            next(csv_reader)  # Saltar la fila de encabezado
            for row in csv_reader:
                marca_tiempo, _ = row  # Tomar la primera columna
                tiempos_idle.append(marca_tiempo)

        # Tomar los dos últimos valores si hay más de dos
        tiempos_idle = tiempos_idle[-2:]

        return tiempos_idle

    except Exception as e:
        print(f"Error al obtener los tiempos idle desde el archivo CSV: {e}")
        return None

def obtener_uso_cpu(worker_info):
    try:
        # Desempaquetar la información del worker
        worker_ip, username, password = worker_info

        # Crear una conexión SSH
        with paramiko.SSHClient() as ssh_client:
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(worker_ip, username=username, password=password)

            # Ejecutar el comando para obtener información de CPU en el worker
            comando_cpu = "top -bn 1 | grep '%Cpu' | awk '{print $2}'"
            resultado_cpu = ssh_client.exec_command(comando_cpu)[1].read().decode().strip()

            # Procesar el resultado según sea necesario
            porcentaje_cpu_usado = max(0, float(resultado_cpu))  # Asegurar que el valor no sea negativo

        return porcentaje_cpu_usado

    except Exception as e:
        print(f"Error al obtener el uso de CPU para {worker_info[0]}: {e}")
        return None

def obtener_informacion_memoria(worker_info):
    try:
        # Desempaquetar la información del worker
        worker_ip, username, password = worker_info

        # Crear una conexión SSH
        with paramiko.SSHClient() as ssh_client:
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(worker_ip, username=username, password=password)

            # Ejecutar el comando para obtener información de memoria en el worker
            comando_memoria = "free | grep Mem | awk {'print $2,$3,$4'}"
            resultado_memoria = ssh_client.exec_command(comando_memoria)[1].read().decode().strip()

            # Procesar el resultado según sea necesario
            valores_memoria = resultado_memoria.split()
            memoria_total, memoria_usada, memoria_libre = map(int, valores_memoria)

        return memoria_total, memoria_usada, memoria_libre

    except Exception as e:
        print(f"Error al obtener información de memoria para {worker_info[0]}: {e}")
        return None

def calcular_tiempo_espera(tiempo_registro1, tiempo_registro2):
    try:
        # Convertir las marcas de tiempo a objetos datetime
        tiempo_dt1 = datetime.strptime(tiempo_registro1, "%Y-%m-%d %H:%M:%S:%f")
        tiempo_dt2 = datetime.strptime(tiempo_registro2, "%Y-%m-%d %H:%M:%S:%f")

        # Calcular la diferencia de tiempo
        diferencia_tiempo = tiempo_dt2 - tiempo_dt1

        # Obtener la diferencia en segundos
        diferencia_segundos = diferencia_tiempo.total_seconds()

        return diferencia_segundos

    except Exception as e:
        print(f"Error al calcular el tiempo de espera: {e}")
        return None

def monitorear_uso_recursos():
    # Lista de workers con sus respectivas direcciones IP, nombres de usuario y contraseñas
    workers = [
        ("10.0.0.30", "ubuntu", "ubuntu"),
        ("10.0.0.40", "ubuntu", "ubuntu"),
        ("10.0.0.50", "ubuntu", "ubuntu")
    ]

    # Tabla consolidada para la memoria de cada worker
    tabla_memoria_consolidada = PrettyTable()
    tabla_memoria_consolidada.field_names = ["Worker", "Memoria Total (KB)", "Memoria Usada (KB)", "Memoria Libre (KB)"]

    # Tabla consolidada para el uso del sistema de cada worker
    tabla_uso_sistema_consolidado = PrettyTable()
    tabla_uso_sistema_consolidado.field_names = ["Worker", "Porcentaje Sistema Usado", "Porcentaje Sistema No Usado", "Cores Usados", "Tiempo de Espera"]

    # Iterar sobre los workers y obtener información de CPU y memoria
    for worker_info in workers:
        tiempos_idle = obtener_tiempos_idle_desde_csv(f"~/monitoreo/worker{workers.index(worker_info) + 1}_tiempos_idle.csv")
        idle_real=obtener_tiempos_idle_desde_csv_Real(f"~/monitoreo/worker{workers.index(worker_info) + 1}_tiempos_idle.csv")
        
        if idle_real is not None and len(idle_real) == 2:
            tiempo_idle1, tiempo_idle2 = idle_real
            print(f"Tiempo Idle 1 para {worker_info[0]}: {tiempo_idle1}")
            print(f"Tiempo Idle 2 para {worker_info[0]}: {tiempo_idle2}")

            if tiempos_idle is not None and len(tiempos_idle) == 2:
                tiempo_registro1, tiempo_registro2 = tiempos_idle
                print(f"Tiempo de Registro 1 para {worker_info[0]}: {tiempo_registro1}")
                print(f"Tiempo de Registro 2 para {worker_info[0]}: {tiempo_registro2}")
                
                cant_cores = 5  

                # Calcular el tiempo de espera
                tiempo_espera = calcular_tiempo_espera(tiempo_registro1, tiempo_registro2)

                if tiempo_espera is not None:
                    print(f"Tiempo de Espera para {worker_info[0]}: {tiempo_espera} segundos")

                    # Calcular los porcentajes según la fórmula proporcionada
                    fraccion_no_usado_sistema = (tiempo_idle2 - tiempo_idle1) / (cant_cores * tiempo_espera * 100)
                    fraccion_usado_sistema = 1 - fraccion_no_usado_sistema
                    core_usados = fraccion_usado_sistema * cant_cores
                    print(fraccion_no_usado_sistema)

                    # Obtener información de memoria y CPU específica del worker
                    memoria_info = obtener_informacion_memoria(worker_info)
                    porcentaje_cpu_worker = obtener_uso_cpu(worker_info)

                    if memoria_info is not None:
                        memoria_total, memoria_usada, memoria_libre = memoria_info

                        # Agregar información a la tabla consolidada de memoria
                        tabla_memoria_consolidada.add_row([worker_info[0], memoria_total, memoria_usada, memoria_libre])

                    if porcentaje_cpu_worker is not None:
                        # Agregar información a la tabla consolidada de uso del sistema
                        tabla_uso_sistema_consolidado.add_row([worker_info[0], round(fraccion_usado_sistema * 100, 2),
                                                            round(fraccion_no_usado_sistema * 100, 2), round(core_usados, 2),
                                                            tiempo_espera])

    # Imprimir tablas consolidadas al final
    print("\nTabla del uso de memoria de cada worker:")
    print(tabla_memoria_consolidada)
    

    print("\nTabla  del uso del sistema de cada worker:")
    print(tabla_uso_sistema_consolidado)
    input("Ingrese Enter...")

# Llamada a la función general
#monitorear_uso_recursos()
