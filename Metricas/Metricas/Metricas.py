import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# Configuración de conexión
server = 'preguntasrec.database.windows.net'
database = 'PreguntasyRespuestas'
username = 'admin2024'
password = 'AdminR2024'
driver = '{ODBC Driver 17 for SQL Server}'

# Crear la cadena de conexión
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def conectar_db():
    """Conectar a la base de datos y retornar la conexión."""
    try:
        conn = pyodbc.connect(conn_str)
        print("Conexión a la base de datos establecida con éxito.")
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def obtener_resultados(conn):
    """Obtener los resultados de la base de datos y retornar un DataFrame."""
    query = "SELECT usuarioID, Correo, tag, puntaje FROM Usuario ORDER BY usuarioID"
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error al consultar resultados: {e}")
        return pd.DataFrame()

def graficar_resultados(df):
    """Graficar los resultados usando matplotlib y mostrar dos gráficos."""
    if df.empty:
        print("No hay datos para graficar.")
        return
    
    plt.figure(figsize=(14, 10))
    
    x = df['usuarioID']
    y = df['puntaje']

    # Verificar si hay suficientes datos para la spline
    if len(x) >= 3:
        x_smooth = np.linspace(x.min(), x.max(), 300)
        spline = make_interp_spline(x, y, k=3)
        y_smooth = spline(x_smooth)
    else:
        x_smooth = x
        y_smooth = y

    # Primer gráfico: Línea con puntajes
    plt.subplot(2, 1, 1)
    plt.plot(x, y, marker='o', linestyle='-', color='b', alpha=0.3, label='Datos Originales')
    if len(x) >= 3:
        plt.plot(x_smooth, y_smooth, color='b', label='Curva Suavizada')
    plt.xlabel('ID de Usuario')
    plt.ylabel('Puntaje')
    plt.title('Gráfico de Puntajes por Usuario')
    
    # Ajustar el límite del eje y
    plt.ylim(0, 100)
    
    plt.grid(True)
    plt.legend()
    
    # Segundo gráfico: Histograma de puntajes con etiquetas (orientación horizontal)
    plt.subplot(2, 1, 2)
    bins = np.arange(0, 101, 10)  # Crear bins de 10 en 10 hasta 100
    counts, bins, patches = plt.hist(df['puntaje'], bins=bins, color='orange', edgecolor='black', orientation='horizontal')
    plt.ylabel('Puntaje')
    plt.xlabel('Frecuencia')
    plt.title('Histograma de Puntajes')
    
    # Añadir etiquetas de usuario al lado de cada barra
    for patch, bin_start, bin_end in zip(patches, bins[:-1], bins[1:]):
        usuarios_en_bin = df[(df['puntaje'] >= bin_start) & (df['puntaje'] < bin_end)]['Correo']
        etiquetas = '\n'.join(usuarios_en_bin)
        height = patch.get_y() + patch.get_height() / 2
        plt.text(patch.get_width(), height, etiquetas, ha='left', va='center', rotation=0)

    plt.xlim(0, max(counts) * 1.2)  # Ajustar el límite del eje x para acomodar las etiquetas
    
    plt.tight_layout()
    plt.show()

# Conectar a la base de datos
conn = conectar_db()

if conn:
    # Obtener los resultados
    df_resultados = obtener_resultados(conn)
    
    # Graficar los resultados
    graficar_resultados(df_resultados)
    
    # Cerrar la conexión
    conn.close()
