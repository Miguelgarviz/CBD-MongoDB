import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURACIÓN ---
CSV_SINGLE = 'mongo-not-sharded/results/not_sharded_results.csv'
CSV_SHARDING = 'mongo-sharded/results/sharded_results.csv'
SALTO = 50  # Ajustable: 1, 5, 10, etc.
# ---------------------

def procesar_csv(nombre_archivo, salto):
    col_names = [
    'timestamp', 'elapsed', 'label', 'responseCode', 'responseMessage', 
    'threadName', 'dataType', 'success', 'failureMessage', 'bytes', 
    'sentBytes', 'grpThreads', 'allThreads', 'URL', 'Latency', 'IdleTime', 'Connect'
]
    
    df = pd.read_csv(nombre_archivo, names=col_names, header=None)
    df['elapsed'] = pd.to_numeric(df['elapsed'], errors='coerce')
    df['allThreads'] = pd.to_numeric(df['allThreads'], errors='coerce')
    df = df[df['success'].astype(str).str.lower() == 'true'].copy()
    
    # Aplicar el salto/muestreo
    df['rango_hilos'] = (df['allThreads'] // salto) * salto
    df.loc[df['rango_hilos'] == 0, 'rango_hilos'] = 1
    
    # Calcular la media por cada salto
    return df.groupby('rango_hilos')['elapsed'].mean().reset_index()

# 1. Cargar y procesar ambos datasets
try:
    stats_single = procesar_csv(CSV_SINGLE, SALTO)
    stats_sharding = procesar_csv(CSV_SHARDING, SALTO)
except FileNotFoundError as e:
    print(f"Error: No se encontró uno de los archivos CSV. {e}")
    exit()

# 2. Crear la gráfica comparativa
plt.figure(figsize=(12, 7))

# Línea Nodo Único
plt.plot(stats_single['rango_hilos'], stats_single['elapsed'], 
         label='Nodo Único (Single Node)', color='#e74c3c', marker='s', linewidth=2.5)

# Línea Sharding
plt.plot(stats_sharding['rango_hilos'], stats_sharding['elapsed'], 
         label='Clúster Sharded (2 Shards)', color='#2ecc71', marker='o', linewidth=2.5)

# Estética profesional
plt.title(f'Comparativa de Rendimiento: Nodo Único vs. Sharding (Muestreo: {SALTO})', fontsize=14)
plt.xlabel('Carga de Usuarios Simultáneos (Threads)', fontsize=12)
plt.ylabel('Tiempo de Respuesta Medio (ms)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# 3. Guardar y mostrar
plt.tight_layout()
plt.savefig('COMPARATIVA_FINAL_RENDIMIENTO_2.png', dpi=300)
plt.show()

print("Gráfica comparativa generada con éxito como 'COMPARATIVA_FINAL_RENDIMIENTO.png'")