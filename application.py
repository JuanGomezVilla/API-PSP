# Importación de Flask, la obtención de argumentos, la conversión a JSON del texto, descarga 
from flask import Flask, request, jsonify, json, Response, render_template
from flask_cors import CORS, cross_origin
import pymysql, pymysql.cursors, openpyxl, hashlib

# Creación de una aplicación y CORS (CONFIGURACIÓN: accesos de orígenes desconocidos, orden de claves)
application = Flask(__name__)
cors = CORS(application)
application.config["CORS_HEADERS"] = "Content-Type"
application.config["JSON_SORT_KEYS"] = False
application.config["JSON_AS_ASCII"] = False

# CONFIGURACIÓN DE LA BASE DE DATOS
ajustes = {
    "hostname": "localhost",
    "dbuser": "root",
    "password": "",
    "dbname": "hashTable"
}

# Clase Utils (los métodos son estáticos, no es necesario crear instancias de la clase)
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
        
    # Procesa el JSON, recibe unos datos, y comprueba si se debe formatearlos
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


# INDEX -----------------------------------------------------------------------------------------------------------
@application.route("/")
def indice_contenidos():
    # Renderiza la página inicial (front)
    return render_template("index.html")


# MÉTODOS GET -----------------------------------------------------------------------------------------------------
@application.route("/api/get/cifrarValor", methods=["GET"])
def cifrarValor():
    # Obtención del valor a cifrar de los argumentos
    palabra = request.args.get("palabra", None, str)
    cifrados = {"md5": None, "sha1": None, "sha2": None}

    # Si la palabra no se ha pasado
    if palabra is None:
        mensaje = "No se ha pasado ninguna palabra"
    else:
        # En caso de desencadenarse un error
        try:
            # Cifra la palabra en los tres tipos de cifrado
            cifrados["md5"] = hashlib.md5(palabra.encode()).hexdigest()
            cifrados["sha1"] = hashlib.sha1(palabra.encode()).hexdigest()
            cifrados["sha2"] = hashlib.sha256(palabra.encode()).hexdigest()

            # Captura posibles filas con ese valor
            filas = Utils.ejecutar_query("SELECT palabra FROM palabras WHERE palabra=%s LIMIT 1", [palabra])

            # Si no existen filas, el valor se puede añadir a la base de datos
            if filas is None:
                # Ejecuta una query con la posibilidad de insertar palabras, notificando que se realiza una acción de insertar
                datos = Utils.ejecutar_query("CALL insertarPalabra(%s)", [palabra], True)
            
            # La palabra está cifrada
            mensaje = "Palabra cifrada"
        except:
            # Mensaje notificando que se ha realizado un error
            mensaje = "Error realizando la acción"
    
    # Devuelve un JSON final
    return Utils.devolver_JSON({"estado":"OK", "mensaje":mensaje, "palabra":palabra, "cifrados":cifrados})

@application.route("/api/get/descifrarHash", methods=["GET"])
def descifrarValor():
    # Obtención del valor a descifrar y creación de una variable palabra resultado
    paramCifradoMD5 = request.args.get("md5", None, str)
    paramCifradoSHA1 = request.args.get("sha1", None, str)
    paramCifradoSHA256 = request.args.get("sha256", None, str)
    palabra = cifradoMD5 = cifradoSHA1 = cifradoSHA256 = None

    # Si no hay valor para cifrar, lo notifica
    if paramCifradoMD5 is None and paramCifradoSHA1 is None and paramCifradoSHA256 is None:
        mensaje = "No se ha pasado ninguna clave a descifrar"
    else:
        # Obtiene un posible valor si existe
        filas = Utils.ejecutar_query("CALL descifrarHash(%s, %s, %s)", [paramCifradoMD5, paramCifradoSHA1, paramCifradoSHA256])
        
        # Posible error de conexión con la base de datos
        if filas == "ERROR":
            mensaje = "Error de servidor"
        elif filas is None:
            mensaje = "Palabra no encontrada"
        else:
            # Si existen filas, la palabra se ha encontrado, y la variable 'palabra' recibe el valor descifrado
            mensaje = "Palabra encontrada"
            palabra = filas[0]["palabra"]
            cifradoMD5 = filas[0]["cifradoMD5"]
            cifradoSHA1 = filas[0]["cifradoSHA1"]
            cifradoSHA256 = filas[0]["cifradoSHA256"]

    # Devuelve un resultado en formato JSON
    return Utils.devolver_JSON({"estado":"OK", "mensaje":mensaje, "palabra":palabra, "cifrados" :{"md5":cifradoMD5, "sha1":cifradoSHA1, "sha256": cifradoSHA256}})


# MÉTODOS POST --------------------------------------------------------------------------------------------
@application.route("/api/post/insertarPalabra", methods=["POST"])
def insertar_palabra():
    # Obtiene la palabra del JSON, un mensaje de devolución y una variable para el estado de la conexión
    datos = request.get_json()
    mensaje = None
    estado = "OK"

    # Intenta obtener los datos del JSON
    try:
        # Guarda la palabra y la conexión
        palabra = datos["palabra"]
        conexion = Utils.obtener_conexion()

        # Si no existe conexión
        if not conexion:
            mensaje = "Servidor inestable"
            estado = "ERROR"
        else:
            # Busca palabras que cumplan dicha coincidencia
            palabras = Utils.ejecutar_query("SELECT palabra FROM palabras WHERE palabra=%s LIMIT 1", [palabra])

            # Si no existen datos
            if not palabras:
                # Inserta la palabra y cambia el mensaje
                Utils.ejecutar_query("CALL insertarPalabra(%s)", [palabra], True)
                mensaje = "Palabra insertada correctamente"
            else:
                # No inserta el dato y menciona la causa
                mensaje = "La palabra ya existe"
    except:
        # Si se desencadena,
        mensaje = "No se ha aportado el parámetro 'palabra'"
        
    # Devuelve el resultado final
    return Utils.devolver_JSON({"estado":estado, "mensaje":mensaje})


# MÉTODO DELETE -----------------------------------------------------------------------------------------------------
@application.route("/api/delete/eliminar", methods=["DELETE"])
def eliminar_clave():
    # Obtención de los datos pasados en JSON, mensaje a devolver, y el estado de la base de datos
    datos = request.get_json()
    mensaje = None
    estado = "OK"

    # Intenta capturar el valor de la clave 'palabra' del JSON, posteriormente captura la conexión si todo es correcto
    try:
        palabra = datos["palabra"]
        conexion = Utils.obtener_conexion()

        # Si existe una conexión
        if conexion:
            # Obtiene todas las palabras con ese valor
            palabras = Utils.ejecutar_query("SELECT palabra FROM palabras WHERE palabra=%s LIMIT 1", [palabra])
            if palabras:
                # Eliminar la clave y notificar con un mensaje el resultado final
                Utils.ejecutar_query("DELETE FROM palabras WHERE palabra = %s", [palabra], True)
                mensaje = "Palabra eliminada con éxito"
            else:
                mensaje = "La palabra a eliminar no existe"
        else:
            mensaje = "Servidor inestable"
            estado = "ERROR"
    except:
        mensaje = "El nombre del parámetro pasado no es correcto"

    # Devuelve un resultado final
    return Utils.devolver_JSON({"estado" : estado, "mensaje" : mensaje})

# MÉTODO PUT --------------------------------------------------------------------------------------------------------
@application.route("/api/put/modificarValorPalabra", methods=["PUT"])
def modificar_valor_palabra():
    # Obtención de los datos pasados en JSON, mensaje a devolver, y el estado de la base de datos
    datos = request.get_json()
    mensaje = None
    estado = "OK"

    # Intenta capturar el valor de la clave 'palabra' del JSON, posteriormente captura la conexión si todo es correcto
    try:
        palabra = datos["palabra"]
        palabraNueva = datos["palabraNueva"]
        conexion = Utils.obtener_conexion()

        # Si existe una conexión
        if conexion:
            # Obtiene todas las palabras con ese valor
            palabras = Utils.ejecutar_query("SELECT palabra FROM palabras WHERE palabra IN (%s, %s) LIMIT 1", [palabra, palabraNueva])
            if palabras:
                # Eliminar la clave y notificar con un mensaje el resultado final
                Utils.ejecutar_query("UPDATE palabras SET palabra = %s WHERE palabra = %s", [palabraNueva, palabra], True)
                mensaje = "Palabra eliminada con éxito"
            else:
                mensaje = "La palabra a eliminar no existe"
        else:
            mensaje = "Servidor inestable"
            estado = "ERROR"
    except:
        mensaje = "El nombre del parámetro pasado no es correcto"

    # Devuelve un resultado final
    return Utils.devolver_JSON({"estado" : estado, "mensaje" : mensaje})