import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURACIÓN ---
archivos = {
    '1 Shard (Single)': 'mongo-sharing/results/sharded_results_1_nodo.csv',
    '2 Shards': 'mongo-sharing/results/sharded_results_2_1_nodos.csv',
    '3 Shards': 'mongo-sharing/results/sharded_results_3_2_nodos.csv'
}

SALTO = 50  # Agrupamos de 50 en 50 usuarios para suavizar las líneas
COLORES = ['#e74c3c', '#f1c40f', '#2ecc71'] # Rojo, Amarillo, Verde (Semáforo de rendimiento)

# Columnas estándar de JMeter para OS Process Sampler
col_names = [
    'timestamp', 'elapsed', 'label', 'responseCode', 'responseMessage', 
    'threadName', 'dataType', 'success', 'failureMessage', 'bytes', 
    'sentBytes', 'grpThreads', 'allThreads', 'URL', 'Latency', 'IdleTime', 'Connect'
]

plt.figure(figsize=(14, 8))

for (etiqueta, ruta), color in zip(archivos.items(), COLORES):
    try:
        # 1. Cargar y limpiar datos
        df = pd.read_csv(ruta, names=col_names, header=None, low_memory=False)
        df['elapsed'] = pd.to_numeric(df['elapsed'], errors='coerce')
        df['allThreads'] = pd.to_numeric(df['allThreads'], errors='coerce')
        
        df_clean = df[(df['success'].astype(str).str.lower() == 'true') & 
                      (df['allThreads'].notna())].copy()

        # 2. Agrupar por rango de usuarios
        df_clean['rango_hilos'] = (df_clean['allThreads'] // SALTO) * SALTO
        df_clean.loc[df_clean['rango_hilos'] == 0, 'rango_hilos'] = 1 
        
        # 3. Calcular la media de tiempo de respuesta
        stats = df_clean.groupby('rango_hilos')['elapsed'].mean().reset_index()

        # 4. Dibujar la línea
        plt.plot(stats['rango_hilos'], stats['elapsed'], 
                 label=etiqueta, color=color, marker='o', linewidth=2.5, markersize=4)
        
    except Exception as e:
        print(f"Error procesando {etiqueta}: {e}")

# --- ESTÉTICA DE LA GRÁFICA ---
plt.title('Comparativa de Escalabilidad Horizontal: Latencia vs. Número de Shards', fontsize=16, pad=20)
plt.xlabel('Carga de Usuarios Simultáneos (Threads)', fontsize=13)
plt.ylabel('Tiempo de Respuesta Medio (ms)', fontsize=13)

# Ajustar el eje X para que coincida con tus 1000 usuarios
plt.xticks(np.arange(0, 1001, 100))
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(title="Infraestructura", fontsize=11)

# Añadir una nota explicativa
plt.text(0, -0.12, f"* Datos promediados en intervalos de {SALTO} usuarios. Menor latencia indica mejor rendimiento.", 
         transform=plt.gca().transAxes, fontsize=10, style='italic')

plt.tight_layout()
plt.savefig('COMPARATIVA_FINAL_SHARDS_4.png', dpi=300)
plt.show()