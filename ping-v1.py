# -*- coding: utf-8 -*-

"""
FASE 1 - TAREA 1.1: Script de Ping Básico

Este script es el primer paso de nuestro proyecto.
Su objetivo es simple:
1. Definir una IP de destino (target).
2. Ejecutar el comando 'ping' del sistema operativo.
3. Mostrar la salida de ese comando en la consola.

Usamos las librerías 'subprocess' y 'platform'.
"""

import subprocess
import platform

def simple_ping(target):
    """
    Ejecuta un simple comando 'ping' al 'target' especificado.
    Se adapta automáticamente a Windows, Linux o macOS.
    """
    
    print(f"--- Iniciando ping a {target} ---")
    
    # Detectamos el sistema operativo para construir el comando correcto
    # platform.system() devuelve "Windows", "Linux", "Darwin" (para macOS), etc.
    current_os = platform.system().lower()
    
    if current_os == "windows":
        # En Windows, '-n' especifica el número de paquetes a enviar.
        # Usamos 4 como un estándar.
        command = ["ping", "-n", "4", target]
    else:
        # En Linux y macOS, '-c' cumple la misma función.
        command = ["ping", "-c", "4", target]

    try:
        # subprocess.run() es la forma moderna de ejecutar comandos del sistema.
        # - command: Es la lista con el comando y sus argumentos.
        # - capture_output=True: Captura la salida estándar (stdout) y el error estándar (stderr).
        # - text=True: Devuelve la salida como texto (string) en lugar de bytes.
        # - check=True: Si el comando falla (devuelve un código de error), lanza una excepción.
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        
        # Si el comando se ejecuta con éxito, mostramos la salida
        print("\n--- Resultados del Ping ---")
        print(result.stdout)
        
        if result.stderr:
            print("\n--- Errores (stderr) ---")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        # Esto se ejecuta si el comando 'ping' falla (ej. la IP no es alcanzable)
        print(f"\nError al ejecutar el ping:")
        print(e.stderr)
    except FileNotFoundError:
        # Esto se ejecuta si el comando 'ping' no se encuentra en el sistema
        print("\nError: No se encontró el comando 'ping' en tu sistema.")
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"\nHa ocurrido un error inesperado: {e}")

# --- Punto de entrada del script ---
if __name__ == "__main__":
    # Definimos la IP a la que queremos hacer ping.
    # 8.8.8.8 es el servidor DNS público de Google, un buen punto de partida.
    target_ip = "8.8.8.8"
    
    # También podrías probar con otros, como el de Cloudflare:
    # target_ip = "1.1.1.1"
    
    simple_ping(target_ip)