import oracledb

def obtener_conexion():

    try:
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=dsn
        )
        print("✅ Conexión exitosa a la base de datos Oracle")
        return connection

    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"❌ Error al conectar: {error.message}")
        return None

