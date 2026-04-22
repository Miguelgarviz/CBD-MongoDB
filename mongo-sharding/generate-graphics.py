import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


SALTO = 50  # Cambia esto: 1 para ver todo, 5, 10, 20 para saltos mayores
MOSTRAR_RELLENO = True

# 1. Definimos las columnas
col_names = [
    'timestamp', 'elapsed', 'label', 'responseCode', 'responseMessage', 
    'threadName', 'dataType', 'success', 'failureMessage', 'bytes', 
    'sentBytes', 'grpThreads', 'allThreads', 'URL', 'Latency', 'IdleTime', 'Connect'
]

# 2. Cargar y limpiar el CSV
df = pd.read_csv('mongo-sharing/results/sharded_results.csv', names=col_names, header=None)
df['elapsed'] = pd.to_numeric(df['elapsed'], errors='coerce')
df['allThreads'] = pd.to_numeric(df['allThreads'], errors='coerce')
df_clean = df[df['success'].astype(str).str.lower() == 'true'].copy()

# 3. AGRUPAR DATOS: Calculamos Min, Max y Media para cada nivel de hilos
# Agrupamos por la columna 'allThreads'
# Creamos una columna nueva que redondea los hilos al salto más cercano
df_clean['rango_hilos'] = (df_clean['allThreads'] // SALTO) * SALTO
# Si el salto es 10, los hilos 1-9 se vuelven 0, 10-19 se vuelven 10... 
# Ajustamos para que no empiece en 0 si no queremos
df_clean.loc[df_clean['rango_hilos'] == 0, 'rango_hilos'] = 1 

# 3. Agrupar por el nuevo rango
stats = df_clean.groupby('rango_hilos')['elapsed'].agg(['min', 'max', 'mean']).reset_index()

# 4. Crear la gráfica
plt.figure(figsize=(12, 7))

# Líneas principales
plt.plot(stats['rango_hilos'], stats['max'], label=f'Máximo (Salto: {SALTO})', color='#e74c3c', marker='v', linestyle=':', alpha=0.7)
plt.plot(stats['rango_hilos'], stats['mean'], label='Media (Promedio)', color='#2980b9', marker='o', linewidth=3)
plt.plot(stats['rango_hilos'], stats['min'], label=f'Mínimo (Salto: {SALTO})', color='#2ecc71', marker='^', linestyle=':', alpha=0.7)

if MOSTRAR_RELLENO:
    plt.fill_between(stats['rango_hilos'], stats['min'], stats['max'], color='gray', alpha=0.1)

# Estética
plt.title(f'Rendimiento MongoDB - Muestreo cada {SALTO} usuarios', fontsize=14)
plt.xlabel('Número de Usuarios (Threads)', fontsize=12)
plt.ylabel('Tiempo de Respuesta (ms)', fontsize=12)
plt.xticks(stats['rango_hilos']) # Forzamos que los números del eje X coincidan con los saltos
plt.grid(True, axis='y', linestyle='--', alpha=0.5)
plt.legend()

# 6. Guardar y mostrar
plt.tight_layout()
plt.savefig('mongo-sharing/graphics/grafica_sharded_2_1.png', dpi=300)
plt.show()