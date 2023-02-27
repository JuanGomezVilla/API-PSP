from flask import Response, request, json
import qrcode, io, pymysql

# CONFIGURACIÓN DE LA BASE DE DATOS
ajustes = {
    "hostname": "localhost", # Nombre de la base de datos
    "dbuser": "root", # Nombre del usuario
    "password": "", # Contraseña del usuario
    "dbname": "hashtable" # Nombre de la tabla
}

# Clase Utils (los métodos son estáticos, no es necesario crear instancias)
class Utils:
    # Devuelve la conexión con la base de datos
    @staticmethod
    def obtener_conexion():
        # Intenta crear una conexión, y en caso de error devuelve nulo
        try:
            return pymysql.connect(host=ajustes["hostname"], user=ajustes["dbuser"], password=ajustes["password"], db=ajustes["dbname"], charset="utf8")
        except:
            return None
    
    # Método para ejecutar consultas
    @staticmethod
    def ejecutar_query(query, argumentos=None, insertar=False):
        # Captura directamente la conexión
        conexion = Utils.obtener_conexion()

        # Si existe conexión
        if conexion:
            # Declara un cursor de lectura del tipo diccionario y ejecuta la query con los argumentos
            cursor = conexion.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, argumentos)

            # Si la acción a realizar es de insertar
            if insertar:
                # Confirma los cambios, y cierra la conexión, devuelve OK
                conexion.commit()
                conexion.close()
                return "OK"
            else:
                # Obtiene todos los datos del cursor y cierra la conexión
                filas = cursor.fetchall()
                conexion.close()

                # Devuelve nulo si la cantidad de filas es 0, de lo contrario las mismas filas
                return None if len(filas) == 0 else filas

        # Devuelve ERROR por defecto
        return "ERROR"
        
    # Procesa el JSON, recibe unos datos, y comprueba si debe formatearlos
    @staticmethod
    def procesar_json(datos):
        # Captura el parámetro formatear por defecto, por defecto false
        if request.args.get("formatear", "false", str) == "true":
            # Devuelve el JSON formateado con una tabulación de 4 espacios
            return json.dumps(datos, indent=4)
        
        # Devuelve el JSON corregido sin formateo
        return json.dumps(datos, separators=(",", ":"))
        
    
    # Devuelve el JSON directamente al cuerpo de la página
    @staticmethod
    def devolver_JSON(datos):
        # Genera la respuesta en formato JSON con los datos formateados si se indica
        return Response(Utils.procesar_json(datos), content_type="application/json; charset=utf-8")
    
    # Crea un QR a partir de un texto y da la posibilidad de compilarlo
    @staticmethod
    def crear_qr(texto, compilar=False):
        # Crear un QR con configuraciones, añadir los datos pasados, ajustar al cuadro
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(texto)
        qr.make(fit=True)

        # Creación de una imagen con fondo blanco y píxeles negros
        archivo = qr.make_image(fill="black", back_color="white")

        # Si el usuario decide compilar la imagen
        if compilar:
            # Compilación del archivo para evitar guardarlo en el directorio
            compilado = io.BytesIO()
            archivo.save(compilado)
            compilado.seek(0)
            # Devuelve la imagen compilada
            return compilado
        
        # Devuelve el archivo por defecto sin compilar
        return archivo