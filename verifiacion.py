import secrets
import smtplib
from email.mime.text import MIMEText
# import os
# from Crypto.Cipher import AES
# from base64 import b64encode

def verificar_cedula(cedula):
    # Verificar que la cédula tenga la longitud correcta
    if len(cedula) != 10:
        return False

    # Verificar que los primeros dos dígitos correspondan a un código de provincia válido
    codigo_provincia = int(cedula[:2])
    if not 1 <= codigo_provincia <= 22:
        return False

    # Verificar que el tercer dígito corresponda a un valor entre 0 y 6 (cedulas) o 9 (ruc)
    tercer_digito = int(cedula[2])
    if tercer_digito not in {0, 1, 2, 3, 4, 5, 6, 9}:
        return False

    # Verificar que el resto de la cédula cumpla con la fórmula de verificación

    suma = 0
    for i in range(9):
        digito = int(cedula[i])
        if i % 2 == 0:
            digito *= 2
            if digito > 9:
                digito -= 9
        suma += digito


    # Aplicar función techo
    techo = (suma // 10 + 1) * 10


    # Calcular dígito verificador
    verificador = techo - suma


    if verificador == 10:
        verificador = 0

    # Comparar con el último dígito de la cédula
    return verificador == int(cedula[-1])

def generate_otp():
    return secrets.token_hex(6)

def send_otp_email(email, otp):
    smtp_server = "smtp.outlook.com"
    port = 587
    sender_email = "willian.suntaxi@hotmail.com"
    sender_password = "Epn201321187"
    receiver_email = email
    message = MIMEText(f"Su OTP es: {otp}")
    message["Subject"] = "OTP para su cuenta"
    message["From"] = sender_email
    message["To"] = receiver_email

    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())