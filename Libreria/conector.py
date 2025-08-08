import oracledb
import os

def obtener_conexion():
    """
    Establece conexión con la base de datos Oracle usando thin mode
    """
    # Get credentials from environment variables or use defaults
    username = os.getenv('DB_USER', 'actuaria')
    password = os.getenv('DB_PASSWORD', 'ydybn8CZYjHQC')
    host = os.getenv('DB_HOST', 'actuaria.c8gecouhgunh.us-east-1.rds.amazonaws.com')
    port = os.getenv('DB_PORT', '1521')
    service_name = os.getenv('DB_SERVICE', 'actuaria')
 
    try:
        # Use thin mode (no Oracle client required)
        connection = oracledb.connect(
            user=username,
            password=password,
            host=host,
            port=port,
            service_name=service_name
        )
        print("✅ Conexión exitosa a la base de datos Oracle (thin mode)")
        return connection
 
    except oracledb.DatabaseError as e:
        print(f"❌ Error al conectar a Oracle: {e}")
        return None
    except Exception as e:
        print(f"❌ Error general al conectar: {e}")
        return None
