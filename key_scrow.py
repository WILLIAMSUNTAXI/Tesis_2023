import pymongo
from flask_pymongo import PyMongo
from flask import Flask
import rsa


# Crea una conexión al servidor de Mongo en localhost en el puerto 27017
client = pymongo.MongoClient('mongodb://localhost:27017/')

db = client.mi_base_de_datos  # Selecciona la base de datos a utilizar

keys_collection = db.keys  # Selecciona la colección que almacenará las claves

# Se debe cambiar la conexión a una base de datos SQL
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'mi_base_de_datos'
app.config['MONGO_COLLECTION'] = 'keys'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mi_base_de_datos'
mongo = PyMongo(app)

def scrow_key(username,pubkey, privkey):
    # Convierte las claves a cadenas de texto en formato pkcs1 para poder almacenarlas en la base de datos
    pubkey_str = pubkey.save_pkcs1().decode('utf-8')
    privkey_str = privkey.save_pkcs1().decode('utf-8')

    # Crea un documento de la clave en la colección
    key_document = {
        'username': username,
        'pubkey': pubkey_str,
        'privkey': privkey_str
    }
    keys_collection.insert_one(key_document)  # Inserta el documento en la colección

def obtenerClaves(username):
    myquery = {"username": username}
    cursor = mongo.db.keys.find(myquery)
    #sql = "select pubkey, privkey from KEYS where user = username"
    pubkeyStr = ''
    privkeyStr = ''

    for documento in cursor:
        pubkeyStr = documento["pubkey"]
        privkeyStr = documento["privkey"]

    # Convertir las claves en formato pkcs1 a objetos RSA
    pubkey = rsa.PublicKey.load_pkcs1(pubkeyStr.encode('utf-8'))
    privkey = rsa.PrivateKey.load_pkcs1(privkeyStr.encode('utf-8'))

    return (pubkey, privkey)
