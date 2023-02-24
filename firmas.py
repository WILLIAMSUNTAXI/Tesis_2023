import rsa
import base64
from key_scrow import obtenerClaves
from flask import request


# Genera un par de claves criptográficas
#(pubkey, privkey) = rsa.newkeys(512)
# user = 'william.suntaxi'
# scrow_key(user,pubkey,privkey)

def sign(message, privkey):
    signature = rsa.sign(message, privkey, 'SHA-256')
    return signature


# Función de verificación de firma digital
def verify(message, signature, pubkey):
    try:
        rsa.verify(message, signature, pubkey)
        return True
    except rsa.pkcs1.VerificationError:
        return False

def verificar_xml(datos):
    # Obtiene el número de firmas existentes en el diccionario
    num_signatures = sum([1 for key in datos.keys() if 'signature' in key])

    # Recorre todas las firmas y claves públicas del diccionario y verifica cada una
    for i in range(1, num_signatures+1):
        # Carga la clave pública desde la cadena de texto
        pubkey = rsa.PublicKey.load_pkcs1(base64.b64decode(datos['pubkey{}'.format(i)]))

        # Obtiene la firma digital del cliente
        signature = base64.b64decode(datos['signature{}'.format(i)])

        # Verifica la firma digital del documento XML recibido
        if not verify(str(datos['xml_document']).encode('utf-8'), signature, pubkey):
            print("La firma digital {} no es válida.".format(i))
            return False

    # Si se verificaron todas las firmas sin problemas, devuelve True
    print("Todas las firmas digitales son válidas.")
    return True


def firmar_xml(datos, privkey, pubkey):
    # Firma el documento XML
    #xml_document = '<root><apellido>SUNTAXI PICHUASAMIN</apellido><ci>1726264961</ci><codigo_dactilar>123</codigo_dactilar><correoElectronico>darimendj@gmail.com</correoElectronico><dias /><direccion>CALLE 111 AVENIDA 103</direccion><domicilio /><fechaNacimiento /><imposiciones /><lugarNacimiento /><nombre>DARIO</nombre><numerocasa /><ocupacion>MANTA</ocupacion><origen /><periodo_desde /><periodo_hasta /><razon_social /><ruc /><select>Soltero</select><telefono>+593983822887</telefono></root>'

    signature = sign(str(datos['xml_document']).encode('utf-8'), privkey)

    # Convierte el objeto de tipo bytes a una cadena de texto
    xml_document_str = datos['xml_document']

    # Encode the signature and public key in base64
    encoded_signature = base64.b64encode(signature).decode('utf-8')
    encoded_pubkey = base64.b64encode(pubkey.save_pkcs1()).decode('utf-8')


    # Obtiene el número de firmas existentes en el diccionario
    num_firmas = sum([1 for key in datos.keys() if 'signature' in key])

    # Agrega las nuevas claves-valor al diccionario
    datos[f'signature{num_firmas+1}'] = encoded_signature
    datos[f'pubkey{num_firmas+1}'] = encoded_pubkey

    # Devuelve el documento XML firmado y la clave pública al cliente
    return {
        'xml_document': xml_document_str,
        **datos
    }

