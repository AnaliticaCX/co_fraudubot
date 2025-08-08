import oracledb

def obtener_conexion():
    username = 'actuaria'
    password = 'ydybn8CZYjHQC'
    dsn = 'actuaria.c8gecouhgunh.us-east-1.rds.amazonaws.com:1521/actuaria' 

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

