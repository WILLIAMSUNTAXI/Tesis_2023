from flask_pymongo import PyMongo
from flask import Flask
import hashlib

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'db_intermedia'
app.config['MONGO_COLLECTION'] = 'coleccion_minimizados'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/db_intermedia'
mongo = PyMongo(app)

def existe_cedula(cedula):
    # Obtener todos los documentos de la colección que contienen el "salt" y el hash de la cédula
    cursor = mongo.db.coleccion_minimizados.find({}, {'salt': 1, 'id': 1})
    # Recorrer cada documento y obtener el "salt" y el hash almacenados
    for documento in cursor:
        salt = documento['salt']
        hash_almacenado = documento['id']
        # Concatenar el "salt" con la cédula que se está verificando
        cedula_salt = salt + cedula
        # Generar el hash de la cédula con la "salt" concatenada
        cedula_hash = hashlib.sha256(cedula_salt.encode()).hexdigest()
        # Comparar el hash generado con el hash almacenado en el documento
        if cedula_hash == hash_almacenado:
            return True
    return False

def insertarDatos(datos):
    mongo.db.coleccion_minimizados.insert_one(datos)



def mostrarDatos():
    # Realiza una consulta para obtener todos los documentos de la colección
    cursor = mongo.db.coleccion_minimizados.find()
    print(cursor)
    for documento in cursor:
         print(documento)

def consultaDatos():
    cursor = mongo.db.coleccion_minimizados.find()
    datos = []
    for documento in cursor:
        datos.append(documento)
    print(datos)
    return  datos
