import xmltodict
import json
import pyodbc
import psycopg2


def insertarDatosABase(xmlDatos):
    jsonRoot = xmltodict.parse(xmlDatos)
    jsonRoot = json.dumps(jsonRoot)
    jsonRoot = json.loads(jsonRoot)

    jsonDatos = jsonRoot['root']

    # cedula = jsonDatos['cedula']
    cedula = jsonDatos['ci']
    # nombres = jsonDatos['nombres']
    nombres = jsonDatos['nombre']
    # apellidos = jsonDatos['apellidos']
    apellidos = jsonDatos['apellido']
    sexo = 'HOMBRE'
    # condicionCiudadano = jsonDatos['condicionCiudadano']
    condicionCiudadano = jsonDatos['ocupacion']
    fechaNacimiento = jsonDatos['fechaNacimiento']
    lugarNacimiento = jsonDatos['lugarNacimiento']
    nacionalidad = jsonDatos['nacionalidad']
    estadoCivil = jsonDatos['estadoCivil']
    #estadoCivil = jsonDatos['select']
    # codigoDactilar = jsonDatos['codigoDactilar']
    codigoDactilar = jsonDatos['codigo_dactilar']

    domicilio = jsonDatos['domicilio']
    # callesDomicilio = jsonDatos['callesDomicilio']
    callesDomicilio = jsonDatos['direccion']
    # numeroCasa = jsonDatos['numeroCasa']
    numeroCasa = jsonDatos['numerocasa']
    telefono = jsonDatos['telefono']
    correoElectronico = jsonDatos['correoElectronico']

    estadoAfiliado = jsonDatos['estadoAfiliado']

    # rucPatronal = jsonDatos['rucPatronal']
    rucPatronal = jsonDatos['ruc']
    sector = jsonDatos['sector']
    # razonSocial = jsonDatos['razonSocial']
    razonSocial = jsonDatos['razon_social']

    origen = jsonDatos['origen']
    # periodoDesde = jsonDatos['periodoDesde']
    periodoDesde = jsonDatos['periodo_desde']
    # periodoHasta = jsonDatos['periodoHasta']
    periodoHasta = jsonDatos['periodo_hasta']
    imposiciones = jsonDatos['imposiciones']
    dias = jsonDatos['dias']

    try:

        connection = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=SERVER1;DATABASE=Registro_Civil_EPN;UID=sa;PWD=smile'
        )
        print("Conexión exitosa...")

        qrInsertRegistroCivil = 'EXEC [SERVER1].[Registro_Civil_EPN].[dbo].[sp_insertarDatosRegistroCivil] \'' + cedula + '\', \'' + nombres + '\', \'' + apellidos + '\', \'' + sexo + '\', \'' + condicionCiudadano + '\', \'' + fechaNacimiento + '\', \'' + lugarNacimiento + '\', \'' + nacionalidad + '\', \'' + estadoCivil + '\', \'' + codigoDactilar + '\', \'' + domicilio + '\', \'' + callesDomicilio + '\', \'' + numeroCasa + '\', \'' + telefono + '\', \'' + correoElectronico + '\''
        print(qrInsertRegistroCivil)

        cursorInsert = connection.cursor()

        cursorInsert.execute(qrInsertRegistroCivil)
        cursorInsert.commit()

        print('Insercion Registro Civil exitosa ' + cedula)

    except Exception as ex:

        print("Error durante la conexión: {}".format(ex))
        print( 'Error de conexion Registro Civil')

    finally:

        connection.close()  # Se cerró la conexión a la BD.
        print("La conexión Registro Civil ha finalizado.")

    try:

        connection = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=SERVER2;DATABASE=IEES_EPN;UID=sa;PWD=smile'
        )
        print("Conexión exitosa...")

        qrInsertIEES = 'EXEC [SERVER2].[IEES_EPN].[dbo].[sp_insertarDatosIEES] \'' + cedula + '\', \'' + estadoAfiliado + '\', \'' + rucPatronal + '\', \'' + sector + '\', \'' + razonSocial + '\', \'' + origen + '\', \'' + periodoDesde + '\', \'' + periodoHasta + '\', ' + imposiciones + ', ' + dias
        print(qrInsertIEES)

        #qrInsertDatosPersonales = 'EXEC [SERVER2].[IEES_EPN].[dbo].[sp_insertarDatosPersonales] \'' + cedula + '\', \'' + estadoAfiliado + '\''
        ##qrInsertDatosPersonales = "INSERT INTO [SERVER1].[Salva_Datos_EPN].[dbo].[Datos_Personales] ([cedula] ,[estado_afiliado]) VALUES ('1726487554','Activo')"
        #print(qrInsertDatosPersonales)
        # qrInsertEmpleador = 'EXECUTE [dbo].[sp_insertarEmpleador] \'' + rucPatronal + '\', \'' + sector + '\', \'' + razonSocial + '\''
        # print(qrInsertEmpleador)
        # qrInsertHistorialSQLServer = 'EXECUTE [dbo].[sp_insertarHistorial] \'' + origen + '\', \'' + periodoDesde + '\', \'' + periodoHasta + '\', ' + imposiciones + ', ' + dias + ', \'' + cedula + '\', \'' + rucPatronal + '\''
        # print(qrInsertHistorialSQLServer)

        cursorInsert = connection.cursor()

        cursorInsert.execute(qrInsertIEES)
        cursorInsert.commit()

        print('\nInsercion IEES exitosa ' + cedula)

    except Exception as ex:

        print("Error durante la conexión: {}".format(ex))
        print(' \nError de conexionen IEES')

    finally:

        connection.close()  # Se cerró la conexión a la BD.
        print("La conexión IEES ha finalizado.")