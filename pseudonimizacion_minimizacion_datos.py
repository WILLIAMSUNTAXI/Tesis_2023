import hashlib
import secrets


def pseudonimizar_cedula(cedula):

    # Generar una cadena hexadecimal (salt) aleatoria y única para cada usuario
    salt_str = secrets.token_hex(32)
    # Concatenar la "salt" con la cédula
    cedula_salt = salt_str + cedula
    # Encriptar la cédula con la "salt" concatenada con SHA-256
    cedula_hash = hashlib.sha256(cedula_salt.encode()).hexdigest()
    return (cedula_hash, salt_str)

def minimizar_datos(data):
    ci_hash, salt = pseudonimizar_cedula(data['ci'])
    # Crear estructura de datos minimizada
    datos_minimizados = {
        'id': ci_hash,
        'nombre': data['nombre'],
        'apellido': data['apellido'],
        'fecha_nacimiento': data['fechaNacimiento'],
        'ciudad': data['lugarNacimiento'],
        'salt': salt
    }
    return datos_minimizados

