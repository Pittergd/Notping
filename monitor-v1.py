# -*- coding: utf-8 -*-

"""
FASE 1 - TAREA 1.2: Monitor de Conexión Básico (Versión 1.4 - Ping TCP)
...
    - Jitter (variabilidad del ping)
    - Pérdida de Paquetes (%)
---

Historial de Cambios (v1.5 - ¡Refactorización Mayor!):
- ELIMINADAS TODAS LAS DEPENDENCIAS EXTERNAS (se quitó 'pytcping').
- MOTIVO: Los repetidos fallos de 'pip install' (mi culpa) y los
  problemas de permisos de administrador con 'ping3' hacían que
  el proyecto fuera frágil.
- NUEVA LÓGICA: El script ahora usa el módulo 'socket' (incluido en
  Python) para crear un "ping" TCP manualmente.
- Se crea un socket, se establece un timeout, y se mide el tiempo
  que tarda 'socket.connect()'.
- VENTAJA: No requiere 'pip install' y NO requiere privilegios
  de Administrador para funcionar.
- El código es más limpio y autocontenido.
    
---
Historial de Cambios (v1.4 - ¡Importante!):
- CAMBIO DE LIBRERÍA: Reemplazado 'ping3' por 'tcpping'.
- MOTIVO: Los servidores de juego (AWS) bloquean pings ICMP (usados por 'ping3'),
  resultando en 100% de pérdida de paquetes.
- 'tcpping' mide la latencia usando una conexión TCP al puerto del juego
  (en este caso, 443), lo cual es mucho más preciso y no es bloqueado.
- Se añadió 'TARGET_PORT' a la configuración.
- Se actualizó el bucle 'run_monitor' para usar 'tcpping'.
- Se ajustó el manejo de excepciones para 'tcpping'.

---
Historial de Cambios (v1.2):
- Corregido un bug en el manejo de excepciones.
- 'ping3.EXCEPTIONS = True' causa que los 'timeouts' lancen una excepción.
- El 'except' genérico estaba tratando los timeouts como errores fatales
  y rompiendo el bucle.
- Ahora, importamos 'ping3.errors' y capturamos 'ping3_errors.Timeout'
  específicamente como un "paquete perdido", y continuamos el bucle.
- Otros 'Exception' (como 'Permission denied') sí romperán el bucle.

---
Historial de Cambios (v1.1):
- Corregido un bug de temporización del bucle.
- El 'timeout' por defecto de ping3 (4s) causaba que el bucle
  tardara 5s en cada paquete perdido.
- Ahora, el 'timeout' de ping3 se establece en PING_INTERVAL.
- Se usa 'time.monotonic()' para asegurar que cada iteración del
  bucle dure exactamente PING_INTERVAL segundos en total.
---
"""
import socket # ¡La única librería de red que necesitamos!
import time
import os
import platform
import statistics
from collections import deque

# --- Configuración ---
TARGET_IP = "52.207.196.200" # IP de Servidor Fortnite (AWS Brasil?)
TARGET_PORT = 443            # Puerto TCP (visto en el Monitor de Recursos)
PING_INTERVAL = 1     # Intervalo entre pings (en segundos)
HISTORY_LENGTH = 60

def clear_screen():
    """Limpia la pantalla de la terminal (compatible con Windows/Linux/Mac)."""
    current_os = platform.system().lower()
    if current_os == "windows":
        os.system('cls')
    else:
        os.system('clear')

def format_ping(ms):
    """Formatea el ping para mostrarlo bonito."""
    if ms is None:
        return "PERDIDO"
    # Redondeamos a 2 decimales
    return f"{ms:.2f} ms"

def tcp_ping_socket(target_ip, target_port, timeout_sec):
    """
    Realiza un "ping" TCP usando la librería 'socket'.
    Mide el tiempo de conexión y lo devuelve en milisegundos.
    Devuelve None si falla (timeout, conexión rechazada, etc.).
    """
    
    # 1. Crear el socket
    # AF_INET = IPv4
    # SOCK_STREAM = TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Establecer el timeout del socket
    # Si la conexión tarda más que esto, lanzará una excepción
    sock.settimeout(timeout_sec)
    
    start_time = time.monotonic()
    
    try:
        # 3. Intentar conectar
        sock.connect((target_ip, target_port))
        
        # 4. Si tiene éxito, calcular latencia
        end_time = time.monotonic()
        latency_ms = (end_time - start_time) * 1000
        return latency_ms
        
    except (socket.timeout, ConnectionRefusedError, socket.gaierror, OSError):
        # 5. Si falla (timeout, rechazado, etc.), devolver None
        return None
        
    finally:
        # 6. Asegurarse de cerrar el socket pase lo que pase
        sock.close()


def run_monitor():
    """Bucle principal del monitor de red."""
    
    # 'deque' es una lista optimizada para añadir y quitar
    # elementos de los extremos rápidamente.
    ping_results = deque(maxlen=HISTORY_LENGTH)
    packets_sent = 0
    packets_lost = 0

    print(f"--- Iniciando monitor TCP para {TARGET_IP}:{TARGET_PORT} ---")
    print("Presiona Ctrl+C para detener.")
    time.sleep(2) # Pausa inicial
    
    try:
        while True:
            # time.monotonic() es un reloj preciso para medir intervalos
            start_time = time.monotonic()
            
            packets_sent += 1
            
            # --- MANEJO DE PING CON SOCKET (SIN DEPENDENCIAS) ---
            
            # Usamos nuestra nueva función
            current_ping_ms = tcp_ping_socket(TARGET_IP, TARGET_PORT, PING_INTERVAL)
            
            if current_ping_ms is None:
                # Paquete perdido
                packets_lost += 1
                ping_results.append(None)
            else:
                # Paquete recibido
                ping_results.append(current_ping_ms)
            
            
            # --- Cálculos de Estadísticas ---
            
            # Filtramos solo los pings exitosos (no 'None')
            valid_pings = [p for p in ping_results if p is not None]
            
            if not valid_pings:
                # Si no hay pings válidos, mostramos info básica
                avg_ping = 0.0
                jitter = 0.0
            else:
                avg_ping = statistics.mean(valid_pings)
                
                # Jitter: Desviación estándar del ping.
                # Mide cuánto "salta" tu ping. Un Jitter bajo es bueno.
                # Necesitamos al menos 2 muestras para calcular la desviación.
                if len(valid_pings) >= 2:
                    jitter = statistics.stdev(valid_pings)
                else:
                    jitter = 0.0
            
            loss_percentage = (packets_lost / packets_sent) * 100
            
            # --- Mostrar en Pantalla ---
            clear_screen()
            print(f"--- Monitor de Red: {TARGET_IP} --- (Ctrl+C para salir)")
            print(f"Paquetes: {packets_sent} enviados, {packets_lost} perdidos ({loss_percentage:.1f}%)")
            print("--------------------------------------------------")
            
            if current_ping_ms is None:
                print(f"Ping Actual  : PAQUETE PERDIDO")
            else:
                print(f"Ping Actual  : {current_ping_ms:.2f} ms") # Ya está en ms
            
            print(f"Ping Promedio: {avg_ping:.2f} ms (últimos {len(valid_pings)} pings)")
            print(f"Jitter       : {jitter:.2f} ms")
            print("--------------------------------------------------")

            # --- CAMBIO IMPORTANTE: Lógica de temporización ---
            
            # Calculamos cuánto tardó todo el bucle (ping + cálculos + print)
            end_time = time.monotonic()
            elapsed_time = end_time - start_time
            
            # Calculamos cuánto necesitamos 'dormir' para que el
            # bucle *total* dure exactamente 'PING_INTERVAL' segundos.
            sleep_duration = PING_INTERVAL - elapsed_time
            
            if sleep_duration > 0:
                time.sleep(sleep_duration)
            
            # Si el bucle tardó MÁS de PING_INTERVAL (p.ej. el timeout)
            # pasar ahora), no dormimos y empezamos la siguiente
            # iteración inmediatamente.
            
    except KeyboardInterrupt:
        # Esto se activa cuando el usuario presiona Ctrl+C
        print("\n--- Monitor detenido por el usuario ---")

# --- Punto de entrada del script ---
if __name__ == "__main__":
    run_monitor()