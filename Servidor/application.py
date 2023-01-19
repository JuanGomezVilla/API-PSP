# Importación de Flask, la obtención de argumentos, y la conversión a JSON del texto
from flask import Flask, request, jsonify

# Se importa las CORS, para realizar llamadas
from flask_cors import CORS, cross_origin

# Creación de una aplicación y unas CORS
application = Flask(__name__)
cors = CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'

# APLICACIÓN SIMPLE
@application.route("/")
def hello_world():
    return "<h1>Hello world</h1>"
    @application.route("/")

@application.route("/<username>")
def return_username(username):
    return username

# APLICACIÓN DE CALCULADORA
@application.route("/calculadora/", methods=['GET'])
def calcular():
    argumento1 = request.args.get("numero1", 0, int)
    argumento2 = request.args.get("numero2", 0, int)
    diccionario = {
        "numero1": argumento1,
        "numero2": argumento2,
        "resultado": argumento1 + argumento2
    }
    return jsonify(diccionario)

# flask --app application.py --debug run

