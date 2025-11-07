# -*- coding: utf-8 -*-

"""
FASE 1 - TAREA 1.3: Script de Traceroute Básico (Versión 1.0)

Este script nos permite ver la "ruta" (los "saltos") que toman
nuestros paquetes de datos para llegar a un servidor de destino.

Usamos el comando 'tracert' (en Windows) o 'traceroute' (Linux/Mac).

Nuevos aprendizajes (v1.0):
- Detección de IPv6: Verificamos si la IP contiene ":" para
  saber si es IPv6.
- Flag de IPv6: El comando 'tracert' de Windows necesita el
  flag '-6' para trazar rutas IPv6.
- Codificación 'oem': Al igual que con 'ping_v1.py', usamos
  'oem' en Windows para evitar errores de codificación Unicode.
"""

import subprocess
import platform

def run_traceroute(target_ip):
    """
    Ejecuta un 'traceroute' al 'target_ip' especificado.
    Se adapta a Windows/Linux y a IPv4/IPv6.
    """
    
    print(f"--- Iniciando traceroute a {target_ip} ---")
    print("Esto puede tardar unos minutos...")
    
    current_os = platform.system().lower()
    
    # Verificamos si la IP es IPv6 (si contiene ':')
    is_ipv6 = ":" in target_ip
    
    encoding_to_use = 'utf-8'  # Default para Linux/macOS

    if current_os == "windows":
        command = ["tracert"]
        if is_ipv6:
            # Añadimos el flag '-6' para forzar IPv6
            command.append("-6")
        
        # Añadimos '-d' para no resolver nombres, es más rápido
        command.append("-d") 
        command.append(target_ip)
        
        # 'oem' es la codificación correcta para la consola de Windows
        encoding_to_use = 'oem'
    else:
        # Comando para Linux/macOS
        command = ["traceroute"]
        if is_ipv6:
            command.append("-6")
            
        command.append(target_ip)

    try:
        # capture_output=True, text=True, encoding=encoding_to_use
        # Usamos 'check=True' para que lance un error si el comando falla
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding=encoding_to_use)
        
        print(f"\n--- Resultados de Traceroute para {target_ip} ---")
        print(result.stdout)
        
        if result.stderr:
            print("\n--- Errores (stderr) ---")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"\nError al ejecutar el traceroute:")
        # Imprimimos el error también con la codificación correcta
        print(e.stdout) # A veces tracert manda error por stdout
        print(e.stderr)
    except FileNotFoundError:
        print(f"\nError: No se encontró el comando '{command[0]}' en tu sistema.")
    except Exception as e:
        print(f"\nHa ocurrido un error inesperado: {e}")

# --- Punto de entrada del script ---
if __name__ == "__main__":
    
    # --- ¡TU MISIÓN! ---
    # 1. Copia la IP "BUENA" (IPv6) de 57ms que encontraste.
    # 2. Pégala en 'IP_BUENA'
    # 3. Guarda y ejecuta el script: python traceroute_v1.py
    # 4. Analiza la salida.
    # 5. Comenta la línea de IP_BUENA, descomenta la de IP_MALA.
    # 6. Guarda y ejecuta el script de nuevo.
    # 7. ¡COMPARA LOS DOS TEXTOS!
    
    # --- TEST A: RUTA BUENA ---
    # Pega aquí la IP de 57ms (la que empieza con 2600:1f1c...)
    IP_BUENA = "3.160.119.115" 
    run_traceroute(IP_BUENA)
    
    print("\n" + "="*40 + "\n")
    
    # --- TEST B: RUTA MALA ---
    IP_MALA = "52.207.196.200"
    run_traceroute(IP_MALA)