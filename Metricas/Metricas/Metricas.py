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

def obtener_metricas(conn):
    """Obtener las métricas de la base de datos y retornar un DataFrame."""
    query = "SELECT * FROM dbo.CustomMetrics ORDER BY MetricTimestamp DESC"
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error al consultar métricas: {e}")
        return pd.DataFrame()

def graficar_metricas(df):
    """Graficar las métricas usando matplotlib y mostrar dos gráficos."""
    if df.empty:
        print("No hay datos para graficar.")
        return
    
    plt.figure(figsize=(14, 10))
    
    # Convertir las fechas a valores numéricos
    df['MetricTimestamp'] = pd.to_datetime(df['MetricTimestamp'])
    df = df.sort_values(by='MetricTimestamp')  # Asegurarse de que los datos están ordenados
    x = (df['MetricTimestamp'] - df['MetricTimestamp'].min()).dt.total_seconds().values
    y = df['MetricValue'].values

    # Crear una spline para suavizar la línea
    spline = make_interp_spline(x, y)
    x_smooth = np.linspace(x.min(), x.max(), 300)
    y_smooth = spline(x_smooth)

    # Primer gráfico: Línea con calificaciones
    plt.subplot(2, 1, 1)
    plt.plot(df['MetricTimestamp'], y, marker='o', linestyle='-', color='b', alpha=0.3, label='Datos Originales')
    plt.plot(df['MetricTimestamp'].min() + pd.to_timedelta(x_smooth, unit='s'), y_smooth, color='b', label='Curva Suavizada')
    plt.xlabel('Fecha y Hora')
    plt.ylabel('Valor de la Métrica')
    plt.title('Gráfico de Calificaciones')
    
    # Ajustar el límite del eje y
    plt.ylim(0, 10)
    
    # Añadir anotaciones para las calificaciones
    for i, row in df.iterrows():
        plt.annotate(f'{row["MetricValue"]}', 
                     (row["MetricTimestamp"], row["MetricValue"]),
                     textcoords="offset points", 
                     xytext=(0,10), 
                     ha='center')
    
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    
    # Segundo gráfico: Histograma de calificaciones
    plt.subplot(2, 1, 2)
    plt.hist(df['MetricValue'], bins=20, color='orange', edgecolor='black')
    plt.xlabel('Valor de la Métrica')
    plt.ylabel('Frecuencia')
    plt.title('Histograma de Calificaciones')
    
    # Ajustar el límite del eje y
    plt.ylim(0, 10)
    
    plt.tight_layout()
    plt.show()

# Conectar a la base de datos
conn = conectar_db()

if conn:
    # Obtener las métricas
    df_metricas = obtener_metricas(conn)
    
    # Graficar las métricas
    graficar_metricas(df_metricas)
    
    # Cerrar la conexión
    conn.close()
