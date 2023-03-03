# IMPORTACIÓN DE LIBRERÍAS
from flask import Flask, request, jsonify, json, render_template, send_file
from flask_cors import CORS, cross_origin
from utils import Utils
import pymysql, pymysql.cursors, hashlib

# CREACIÓN Y CONFIGURACIÓN DE LA APLICACIÓN
application = Flask(__name__)
cors = CORS(application)
application.config["CORS_HEADERS"] = "Content-Type" # Permitir el acceso desde fuentes desconocidas
application.config["JSON_SORT_KEYS"] = False # Evitar el orden de claves de un JSON
application.config["JSON_AS_ASCII"] = False # Evitar palabras en formato ASCII

# INDEX -----------------------------------------------------------------------------------------------------------
@application.route("/")
def indice_contenidos():
    # Renderiza la página inicial (front)
    return render_template("index.html")



# MÉTODOS GET -----------------------------------------------------------------------------------------------------
@application.route("/api/get/cifrarValor", methods=["GET"])
def cifrarValor():
    # Obtención del valor a cifrar de los argumentos y creación de un diccionario por defecto
    palabra = request.args.get("palabra", None, str)
    cifrados = {"md5": None, "sha1": None, "sha2": None}

    # Si la palabra no se ha pasado
    if palabra is None:
        mensaje = "No se ha pasado ninguna palabra"
    else:
        # Captura posibles errores
        try:
            # Cifra la palabra en los tres tipos de cifrado
            cifrados["md5"] = hashlib.md5(palabra.encode()).hexdigest()
            cifrados["sha1"] = hashlib.sha1(palabra.encode()).hexdigest()
            cifrados["sha2"] = hashlib.sha256(palabra.encode()).hexdigest()

            # Captura una sola fila con ese posible valor, utilizando LIMIT
            filas = Utils.ejecutar_query("SELECT palabra FROM palabras WHERE palabra=%s LIMIT 1", [palabra])

            # Si no existen filas, el valor se puede añadir a la base de datos
            if filas is None:
                # Ejecuta una query con la posibilidad de insertar palabras, notificando que se realiza una acción de commit
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
    # Obtención del valor a descifrar y creación de una variable palabra para el resultado
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

@application.route("/api/get/crearQR", methods=["GET"])
def index():
    # Obtiene una palabra, la cifra y crea un resultado por defecto con el valor de ERROR, aunque no haya sucedido
    palabra = request.args.get("palabra", None, str)
    cifradoMD5 = hashlib.md5(palabra.encode()).hexdigest()
    resultado = "ERROR"

    # Si el cifrado de MD5 contiene datos y la cantidad de caracteres es de 32
    if cifradoMD5 is not None and len(cifradoMD5) == 32:
        # Fija el resultado el valor del cifrado
        resultado = cifradoMD5
    
    # Le pasa el resultado a una función para crear un QR y lo imprime sin necesidad de guardarlo en el servidor
    return send_file(Utils.crear_qr(resultado, True), mimetype="image/png")



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
            # Busca palabras que cumplan dicha coincidencia, aunque solo devolverá un máximo de 1
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
        # Si se desencadena un error, es porque no se ha aportado una palabra
        mensaje = "No se ha aportado el parámetro 'palabra'"
        
    # Devuelve el resultado final
    return Utils.devolver_JSON({"estado":estado, "mensaje":mensaje})



# MÉTODO DELETE -----------------------------------------------------------------------------------------------------
@application.route("/api/delete/eliminarPalabra", methods=["DELETE"])
def eliminar_clave():
    # Obtención de los datos pasados en JSON, mensaje a devolver, y el estado de la base de datos
    datos = request.get_json()
    mensaje = None
    estado = "OK"

    # Intenta capturar el valor de la clave 'palabra' del JSON, posteriormente captura la conexión si todo es correcto
    try:
        # Captura los datos y la conexión con la base de datos
        palabra = datos["palabra"]
        conexion = Utils.obtener_conexion()

        # Si existe una conexión con la base de datos
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
@application.route("/api/put/modificarPalabra", methods=["PUT"])
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
            # Obtiene si existe esa palabra a modificar y si la nueva no existe
            palabraExistir = Utils.ejecutar_query("SELECT palabra FROM palabras WHERE palabra = %s LIMIT 1", [palabra])
            palabraNuevaExistir = Utils.ejecutar_query("SELECT palabra FROM palabras WHERE palabra = %s LIMIT 1", [palabraNueva])
            
            # Si existe una palabra a modificar y el nuevo valor no existe
            if palabraExistir and palabraNuevaExistir is None:
                # Ejecuta un comando de actualización
                Utils.ejecutar_query("UPDATE palabras SET palabra = %s WHERE palabra = %s", [palabraNueva, palabra], True)
                mensaje = "Palabra modificada con éxito"
            else:
                mensaje = "La palabra no existe o ya existe otra con ese valor"
        else:
            mensaje = "Servidor inestable"
            estado = "ERROR"
    except:
        mensaje = "El nombre del parámetro pasado no es correcto"

    # Devuelve un resultado final
    return Utils.devolver_JSON({"estado": estado, "mensaje" : mensaje})

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=6000)