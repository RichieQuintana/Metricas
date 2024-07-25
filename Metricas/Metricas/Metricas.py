import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from collections import defaultdict

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
    
    # Primer gráfico: Línea con puntajes
    x = df['usuarioID'].values
    y = df['puntaje'].values
    
    if len(x) >= 3:
        x_smooth = np.linspace(x.min(), x.max(), 300)
        spline = make_interp_spline(x, y, k=3)
        y_smooth = spline(x_smooth)
    else:
        x_smooth = x
        y_smooth = y

    plt.subplot(2, 1, 1)
    plt.plot(x, y, marker='o', linestyle='-', color='b', alpha=0.3, label='Datos Originales')
    if len(x) >= 3:
        plt.plot(x_smooth, y_smooth, color='b', linestyle='--', label='Curva Suavizada')
    plt.xlabel('ID de Usuario')
    plt.ylabel('Puntaje')
    plt.title('Gráfico de Puntajes por Usuario')
    
    plt.ylim(0, 100)
    plt.grid(True)
    plt.legend()
    
    # Segundo gráfico: Barras con puntuaciones y etiquetas (tag) como barras
    plt.subplot(2, 1, 2)
    x = df['usuarioID']
    y = df['puntaje']
    tags = df['tag']
    
    # Obtener una lista única de tags y asignarles un color
    unique_tags = tags.unique()
    colors = plt.cm.get_cmap('tab20', len(unique_tags))  # Cambia el colormap si hay muchos usuarios
    
    color_map = {tag: colors(i) for i, tag in enumerate(unique_tags)}
    bar_colors = [color_map[tag] for tag in tags]
    
    plt.bar(x, y, color=bar_colors, edgecolor='black')

    # Añadir etiquetas de usuario sobre cada barra
    for i in range(len(x)):
        plt.text(x[i], y[i] + 0.5, tags.iloc[i], ha='center', va='bottom', rotation=90)

    plt.xlabel('ID de Usuario')
    plt.ylabel('Puntuación')
    plt.title('Puntuación de Usuarios')
    
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
