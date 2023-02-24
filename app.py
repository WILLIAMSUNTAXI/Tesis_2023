import uuid
import requests
from QueryWebServer import obtenerDatosSqlServerXML
from almacentamiento import insertarDatosABase
from autorizacion import enviar_solicitud
from flask import Flask, url_for, session, render_template, request, redirect, Response
import xml.etree.ElementTree as ET
import bd_intermedia
from bd_intermedia import insertarDatos,consultaDatos
from firmas import firmar_xml, verificar_xml
from verifiacion import verificar_cedula, generate_otp, send_otp_email
from pseudonimizacion_minimizacion_datos import minimizar_datos
from flask_pymongo import PyMongo
import ssl
from key_scrow import obtenerClaves
from OpenSSL import crypto
import  json
import urllib3
urllib3.disable_warnings()

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['MONGO_DBNAME'] = 'mi_base_de_datos'
app.config['MONGO_COLLECTION'] = 'login'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mi_base_de_datos'
mongo = PyMongo(app)



# Configura la clave secreta de la sesión
app.secret_key = "12345Epn"
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/formulario', methods=['GET', 'POST'])
def hello_world():  # put application's code here
    if request.method == 'POST':
        # Obtenemos la cédula del formulario
        cedula = request.form['ci']
        # Verificamos si la cédula es válida
        if verificar_cedula(cedula):
            data = request.form
            session["datos"] = data
            return redirect(url_for("aceptarTerminos"))
        else:
            # Si no es válida, volvemos a mostrar el formulario
            return render_template('form.html', error=True)
    else:
        # Si es una petición GET, simplemente mostramos el formulario
        return render_template('form.html')

@app.route('/externa', methods=['GET', 'POST'])
def vistaExterna():
    baseDatos = consultaDatos()
    return  render_template('externa.html', baseDatos= baseDatos)


@app.route('/terminos_codiciones', methods=['POST', 'GET'])
def aceptarTerminos():
    return render_template('notificación.html')

@app.route('/solicitar_permiso', methods=['POST'])
def solicitar_permiso():
    datos = request.form

    # Generar un token aleatorio y agregarlo a la lista de solicitudes pendientes
    token = str(uuid.uuid4())
    #solicitudes_pendientes[token] = (nivel_autorizacion, False)
    # Enviar un correo electrónico con un enlace que incluya el token
    enviar_solicitud(datos, token)

    return redirect(url_for('solicitud_enviada'))

@app.route('/solicitud_enviada')
def solicitud_enviada():
  return render_template('solicitud_enviada.html')

@app.route("/autorizar_permiso/<token>")
def autorizar_permiso(token):
    # Verificar si el token está en la lista de solicitudes pendientes


    # Mostrar la página con los botones "Aceptar" y "Denegar"
    return render_template("autorizar_permiso.html", token=token)

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/login_externa', methods= ['GET','POST'])
def login_externa():
    users = mongo.db.login
    #username = request.form['username']
    #login_user = users.find_one({'username': username})
    user_cert = request.files['file']
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, user_cert.read())
    usuario = request.form['username']
    if usuario:
        login_user = users.find_one({'username': usuario})
        if login_user:
            subject = cert.get_subject()
            email = subject.emailAddress
            priv = login_user['privkey']
            priv_bytes = bytes(priv[2:-1], 'utf-8')
            pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, priv_bytes)

            certUser = login_user['certificate']
            certUser_bytes = bytes(certUser[2:-1], 'utf-8')
            cert2 = crypto.load_certificate(crypto.FILETYPE_PEM, certUser_bytes)

            # Agregar el certificado autofirmado a la cadena de confianza
            store = crypto.X509Store()
            store.add_cert(cert)

            # Verificar el certificado con la cadena de confianza
            try:
                crypto.X509StoreContext(store, cert).verify_certificate()
                pkey.check()
                print('El certificado es válido.')
                # comparar huellas de los certificados
                if cert.digest("sha256") == cert2.digest("sha256"):
                    print("Los certificados son iguales")
                    otp = generate_otp()
                    send_otp_email(email, otp)
                    #Cuando se acepte la solicitud se debe enviar el nivel en una session
                    #se hace el update tomando en cuenta el nivel
                    users.update_one({'username': usuario}, {'$set': {'otp': otp}})
                    session["usuario"] = usuario
                    return  redirect(url_for('otp'))
                else:
                    print("Los certificados son diferentes")

            except crypto.Error as e:
                print('El certificado es inválido: {}'.format(str(e)))
            else:
                print("El usuario no existe")
        else:
            print("No se especificó un nombre de usuario")

    # if login_user:
    #     if verify_certificate_with_private_key(cert, login_user['privkey']):
    #     #if request.form['password'].encode('utf-8') == login_user['password'].encode('utf-8'):
    #         otp = generate_otp()
    #         send_otp_email(email, otp)
    #         #Cuando se acepte la solicitud se debe enviar el nivel en una session
    #         #se hace el update tomando en cuenta el nivel
    #         users.update_one({'username': username}, {'$set': {'otp': otp}})
    #         return  redirect(url_for('otp'))
    #         #return  "ENTRÓ"
    return  redirect(url_for('login'))

@app.route("/otp", methods=["GET", "POST"])
def otp():
    return render_template('verify_otp.html')


@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        # Obtener el OTP ingresado por el usuario a partir del formulario
        otp = request.form.get("otp")
        usuario = session.get("usuario")
        users = mongo.db.login
        login_user = users.find_one({'username': usuario})
        # Verificar el OTP con la información almacenada en el servidor


        if otp == login_user['otp']:

            return redirect(url_for("obtener_datos"))
        else:
            # Si el OTP no es válido, mostrar un mensaje de error
            return render_template("verify_otp.html", error="OTP inválido")



@app.route('/confirmacion')
def confirmacion():
    datos = session.get("datos")
    root = ET.Element('root')
    for key, value in datos.items():
        element = ET.SubElement(root, key)
        element.text = value
    xml_str = ET.tostring(root, encoding='utf-8')
    with open('archivo.xml', 'wb') as f:
        f.write(xml_str)
    if bd_intermedia.existe_cedula(datos['ci']):
        return "Ya existe este usuario"
    else:
        insertarDatos(minimizar_datos(datos))
        #Obtener claves del keyscrow
        (pubkey, privkey) = obtenerClaves("william.suntaxi")
        xml_dict = {'xml_document': xml_str.decode('utf-8')}
        xml_firmado_william = firmar_xml(xml_dict,privkey,pubkey)
        cert = ('certificados/cert.pem', 'certificados/key.pem')
        #url = 'http://127.0.0.1:5000/recibirDanny'
        url = 'https://127.0.0.1/recibirDanny'
        headers = {'Content-type': 'application/json'}
        response = requests.post(url,
                                 data=json.dumps(xml_firmado_william),
                                 headers=headers,
                                 #cert=cert,
                                 verify=False
                                 )
        if response.status_code == 200:
            print("Datos enviados exitosamente.")
        else:
            print("Error al enviar los datos: %s" % response.text)

        return "La info se guardó"
    #return render_template('infoGuardada.html')


@app.route('/recibirDanny',methods = ['POST'])
def recibirDanny():
    # Recibir el XML como un diccionario
    xml_firmado_william = request.get_json()
    if verificar_xml(xml_firmado_william):
        (pubkey2, privkey2) = obtenerClaves("danny.venegas")
        xml_firmado_danny = firmar_xml(xml_firmado_william, privkey2, pubkey2)
        cert = ('certificados/cert.pem', 'certificados/key.pem')
        #url = 'http://127.0.0.1:5000/recibirCris'
        url = 'https://127.0.0.1/recibirCris'
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(xml_firmado_danny),
                                 headers=headers,
                                 #cert=cert,
                                 verify = False
                                 )
        if response.status_code == 200:
            print("Datos enviados exitosamente.")
        else:
            print("Error al enviar los datos: %s" % response.text)
    return "Respuesta válida"

@app.route('/recibirCris',methods = ['POST'])
def recibirCris():
    # Recibir el XML como un diccionario
    xml_firmado_danny = request.get_json()
    if verificar_xml(xml_firmado_danny):
        print("SE VERIFICÓ LAS 2 FIRMAS\n-----------------\nSe inserta a la base")
        #insert en la base de datos fragmentada
        insertarDatosABase(str(xml_firmado_danny['xml_document']))
    return "Respuesta válida"

@app.route('/lectura')
def lectura():
    datos = obtenerDatos()
    return render_template('datosXML.html',datos= datos)

def obtenerDatos():
    datos=[]
    tree = ET.parse('datos.xml')
    root = tree.getroot()
    for registro in root:
        registro_dict = {}
        for campo in registro:
            registro_dict[campo.tag] = campo.text
        datos.append(registro_dict)
    return datos


@app.route('/datos')
def obtener_datos():
    # Llamar la función y pasar los parámetros necesarios
    #cedula = "1726264961"
    #SQL = "SELECT nombres, apellidos, lugar_nacimiento FROM Persona where cedula = \'"+ str(cedula) + "\'"
    usuario = session.get("usuario")
    if usuario == 'empresa1':

        #Nivel 1
        SQL = 'SELECT * FROM v_obtenerDatosNivelUno'
        #Nivel 2
        #SQL = 'SELECT * FROM v_obtenerDatosNivelDos'
    if usuario == 'empresa2':
        #Nivel 3
        SQL = 'SELECT * FROM v_obtenerDatosNivelTres'
        #Nivel 4
        #SQL = 'SELECT * FROM v_obtenerDatosNivelCuatro'
    if usuario == 'empresa3':
        #Nivel 5
        SQL =  'SELECT * FROM v_obtenerDatosNivelCinco'
    datos_xml = obtenerDatosSqlServerXML('SERVER1', 'Salva_Datos_EPN', 'sa', 'smile', SQL)
    #datos_xml = obtenerDatosSqlServerXML('172.28.32.52', 'mi_bd', 'sa', 'smile', "SELECT * FROM persona")
    # Devolver los datos XML con el tipo de contenido adecuado
    return Response(datos_xml, mimetype='text/xml')



if __name__ == '__main__':
    print("***----------------------------------------------------------------***")
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('certificados/cert.pem', 'certificados/key.pem')
    app.run(debug=True, port=443, ssl_context=context)


