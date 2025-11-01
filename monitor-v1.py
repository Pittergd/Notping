# -*- coding: utf-8 -*-

"""
FASE 1 - TAREA 1.2: Monitor de Conexión Básico (Versión 1.2 - Corregida)
...
3. Calcular y mostrar estadísticas vitales:
    - Ping Actual
    - Ping Promedio
    - Jitter (variabilidad del ping)
    - Pérdida de Paquetes (%)

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

import ping3
from ping3 import errors as ping3_errors # Importamos los errores de ping3
import time
import os
import platform
import statistics
from collections import deque

# --- Configuración ---
TARGET_IP = "8.8.8.8"
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
    # Redondeamos a 2 decimales y convertimos a milisegundos
    return f"{ms * 1000:.2f} ms"

def run_monitor():
    """Bucle principal del monitor de red."""
    
    # 'deque' es una lista optimizada para añadir y quitar
    # elementos de los extremos rápidamente.
    ping_results = deque(maxlen=HISTORY_LENGTH)
    packets_sent = 0
    packets_lost = 0

    # Cambiamos la unidad de 'ping3' a milisegundos para mayor precisión
    ping3.EXCEPTIONS = True # Queremos que 'ping3' lance errores si algo va mal

    print(f"--- Iniciando monitor de red para {TARGET_IP} ---")
    print("Presiona Ctrl+C para detener.")
    time.sleep(2) # Pausa inicial

    try:
        while True:
            # time.monotonic() es un reloj preciso para medir intervalos
            start_time = time.monotonic()
            
            packets_sent += 1
            
            # --- MANEJO DE ERRORES MEJORADO ---
            try:
                # 1. Intentamos hacer ping
                latency_sec = ping3.ping(TARGET_IP, unit='s', timeout=PING_INTERVAL)
                
                # 2. Si tiene éxito (no hay excepción), es un paquete RECIBIDO
                current_ping_ms = latency_sec * 1000
                ping_results.append(current_ping_ms)
                
            except ping3_errors.Timeout:
                # 3. Si falla por Timeout, es un paquete PERDIDO
                #    ¡Esto es lo que queríamos!
                packets_lost += 1
                ping_results.append(None)
                current_ping_ms = None
                
            except Exception as e:
                # 4. Si falla por CUALQUIER OTRA COSA (permisos, etc.),
                #    es un error fatal y detenemos el monitor.
                clear_screen()
                print(f"Error fatal al ejecutar ping: {e}")
                print("\nEn Windows y Linux, 'ping3' puede requerir")
                print("privilegios de Administrador / root para funcionar.")
                print("Asegúrate de ejecutar como Administrador.")
                break # Salir del bucle
            
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
                print(f"Ping Actual  : {current_ping_ms:.2f} ms")
            
            print(f"Ping Promedio: {avg_ping:.2f} ms (últimos {len(valid_pings)} pings)")
            print(f"Jitter       : {jitter:.2f} ms")
            print("--------------------------------------------------")

            # --- CAMBIO IMPORTANTE: Lógica de temporización ---
            # Reemplazamos el 'time.sleep(PING_INTERVAL)'
            
            # Calculamos cuánto tardó todo el bucle (ping + cálculos + print)
            end_time = time.monotonic()
            elapsed_time = end_time - start_time
            
            # Calculamos cuánto necesitamos 'dormir' para que el
            # bucle *total* dure exactamente 'PING_INTERVAL' segundos.
            sleep_duration = PING_INTERVAL - elapsed_time
            
            if sleep_duration > 0:
                time.sleep(sleep_duration)
            
            # Si el bucle tardó MÁS de PING_INTERVAL (lo que no debería
            # pasar ahora), no dormimos y empezamos la siguiente
            # iteración inmediatamente.
            
    except KeyboardInterrupt:
        # Esto se activa cuando el usuario presiona Ctrl+C
        print("\n--- Monitor detenido por el usuario ---")

# --- Punto de entrada del script ---
if __name__ == "__main__":
    run_monitor()
