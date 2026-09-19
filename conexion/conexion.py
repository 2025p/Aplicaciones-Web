import os
import psycopg2
from psycopg2.extras import RealDictCursor

def obtener_conexion():
    try:
        # Lee la variable de Render; si no existe, usa tus datos locales
        db_url = os.environ.get('DATABASE_URL')
        
        if db_url:
            # Si Render entrega 'postgres://', corregimos a 'postgresql://'
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(db_url, options="-c client_min_messages=warning")
        else:
            # Conexión local de respaldo
            conn = psycopg2.connect(
                host="localhost",
                database="alamoda_db",
                user="postgres",
                password="1234",
                port="5432",
                client_encoding="utf8",
                options="-c client_min_messages=warning"
            )
        return conn
    except Exception as e:
        print("\n" + "="*50)
        print(f"ERROR DE CONEXIÓN: {e}")
        print("="*50 + "\n")
        raise e