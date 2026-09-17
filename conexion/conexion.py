import psycopg2
from psycopg2.extras import RealDictCursor

def obtener_conexion():
    try:
        # Forzamos la conexión a hablar en UTF-8 y codificación en español
        conn = psycopg2.connect(
            host="localhost",
            database="alamoda_db",
            user="postgres",
            password="1234",  # <-- Clave de pgAdmin
            port="5432",
            client_encoding="utf8",
            options="-c client_min_messages=warning"
        )
        return conn
    except Exception as e:
        # Para evitar que Python se caiga con UnicodeDecodeError
        print("\n" + "="*50)
        print("ERROR REAL DE CONEXIÓN A POSTGRESQL:")
        print(e)
        print("="*50 + "\n")
        raise e