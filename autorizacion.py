import smtplib
from email.mime.text import MIMEText

from flask import request


def enviar_solicitud(datos, token):
    correos_autorizados = {
        1: "william.suntaxi.2023@gmail.com",
        2: "william.suntaxi.2023@hotmail.com",
        3: "usuario3@example.com",
        4: "usuario4@example.com",
        5: "usuario5@example.com",
    }
    correo = datos["email"]
    ruc = datos["ruc"]
    cedula = datos["cedula"]
    nivel_autorizacion = datos["nivel_autorizacion"]
    link = f"http://{request.host}/autorizar_permiso/{token}"
    remitente = "pruebas.easy@hotmail.com"
    contrasena = "E@sysoft"
    asunto = "Solicitud de autorización de nivel {}".format(nivel_autorizacion)
    mensaje = "Estimado usuario,\n\nSe ha solicitado una autorización de nivel {} para la empresa de RUC '{}', responder al correo '{}'. Esta empresa quiere realizar una consutla con el parámetro de cédula: '{}'. Por favor, acceda al siguiente enlace:\n{}\n\nAtentamente,\nEl equipo de la aplicación.".format(
        nivel_autorizacion, ruc, correo, cedula, link)
    destinatarios = correos_autorizados[int(nivel_autorizacion)]

    msg = MIMEText(mensaje)
    msg['Subject'] = asunto
    msg['From'] = remitente
    msg['To'] = destinatarios

    server = smtplib.SMTP('smtp.outlook.com', 587)
    server.starttls()
    server.login(remitente, contrasena)
    server.sendmail(remitente, destinatarios, msg.as_string())
    server.quit()
