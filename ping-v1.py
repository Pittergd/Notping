"""
FASE 1 - TAREA 1.1: Script de Ping Básico (Versión 1.1 - Corregida)

Este script es el primer paso de nuestro proyecto.
Su objetivo es simple:
1. Definir una IP de destino (target).
2. Ejecutar el comando 'ping' del sistema operativo.
3. Mostrar la salida de ese comando en la consola.

Usamos las librerías 'subprocess' y 'platform'.

---
Historial de Cambios (v1.1):
- Corregido un 'UnicodeDecodeError' en Windows.
- El comando 'ping' en Windows no devuelve texto en UTF-8, sino en la
  codificación de consola local (ej. cp850).
- Usamos 'oem' como el 'encoding' para Windows, que es el alias de Python
  para la codificación de consola correcta.
- Mantenemos 'utf-8' para sistemas Linux/macOS.
---
"""

import subprocess
import platform

def simple_ping(target):
    """
    Ejecuta un simple comando 'ping' al 'target' especificado.
    Se adapta automáticamente a Windows, Linux o macOS y su codificación.
    """
    
    print(f"--- Iniciando ping a {target} ---")
    
    current_os = platform.system().lower()
    
    encoding_to_use = 'utf-8'  # Default para Linux/macOS

    if current_os == "windows":
        command = ["ping", "-n", "4", target]
        # 'oem' es la codificación correcta para la consola de Windows
        encoding_to_use = 'oem'
    else:
        command = ["ping", "-c", "4", target]

    try:
        # Usamos la variable 'encoding_to_use' que definimos
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding=encoding_to_use)
        
        print("\n--- Resultados del Ping ---")
        print(result.stdout)
        
        if result.stderr:
            print("\n--- Errores (stderr) ---")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"\nError al ejecutar el ping (la IP puede no ser alcanzable):")
        # Imprimimos el error también con la codificación correcta
        print(e.stderr)
    except FileNotFoundError:
        print("\nError: No se encontró el comando 'ping' en tu sistema.")
    except Exception as e:
        print(f"\nHa ocurrido un error inesperado: {e}")

# --- Punto de entrada del script ---
if __name__ == "__main__":
    target_ip = "8.8.8.8"
    simple_ping(target_ip)