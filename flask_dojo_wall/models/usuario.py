import os
# from re import T
# from tkinter import ttk
from flask import flash
from datetime import datetime
from flask_dojo_wall.config.mysqlconnection import connectToMySQL
from flask_dojo_wall.config.myfunctions import diferencia_tiempo
from flask_dojo_wall.models import modelo_base
from flask_dojo_wall.models import mensaje
from flask_dojo_wall.utils.regex import REGEX_CORREO_VALIDO

class Usuario(modelo_base.ModeloBase):

    modelo = 'usuarios'
    campos = ['usuario', 'nombre','apellido','email','password']

    def __init__(self, data):
        self.id = data['id']
        self.usuario = data['usuario']
        self.nombre = data['nombre']
        self.apellido = data['apellido']
        self.email = data['email']
        self.password = data['password']
        self.mensajes_enviados = []
        self.mensajes_recibidos = []
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def buscar(cls, dato):
        query = "select * from usuarios where usuario = %(dato)s OR email = %(dato)s"
        data = { 'dato' : dato }
        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)

        if len(results) < 1:
            return False
        return cls(results[0])


    @classmethod
    def get_usuarios_enviar(cls, dato):

        query = "select * from usuarios where id <> %(id)s"

        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, dato)


        all_data = []

        if results:
            #convertimos la lista de json (diccionarios) en una lista de objetos python
            for data in results:
                all_data.append(cls(data))

        return all_data


    @classmethod
    def update(cls,data):
        query = """UPDATE usuarios
                        SET nombre = %(nombre)s,
                        SET apellido = %(apellido)s,
                        SET email = %(email)s,
                        SET password = %(password)s,
                        SET usuario = %(usuario)s,
                        updated_at=NOW()
                    WHERE id = %(id)s"""
        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        # print("RESULTADO: ", resultado)
        return resultado

    @classmethod
    def update_password(cls,data):
        query = """UPDATE usuarios
                        SET password = %(password_reg)s,
                        updated_at=NOW()
                    WHERE id = %(id)s"""
        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        # print("RESULTADO: ", resultado)
        return resultado


    @staticmethod
    def validar_largo(data, campo, largo):
        is_valid = True
        if len(data[campo]) <= largo:
            flash(f'El largo del {campo} no puede ser menor o igual {largo}', 'error')
            is_valid = False
        return is_valid

    @classmethod
    def validar(cls, data):

        is_valid = True
        #se crea una variable no_create para evitar la sobre escritura de la variable is_valid
        #pero a la vez se vean todos los errores al crear el usuario
        #y no tener que hacer un return por cada error
        no_create = is_valid

        if 'user' in data:
            is_valid = cls.validar_largo(data, 'user', 3)

            if is_valid == False: no_create = False

            if cls.validar_existe('usuario', data['user']):
                flash('el usuario ya esta ingresado', 'error')
                is_valid = False

            if is_valid == False: no_create = False


        if 'name' in data:
            is_valid = cls.validar_largo(data, 'name', 1)
            if is_valid == False: no_create = False

        if 'lastname' in data:
            is_valid = cls.validar_largo(data, 'lastname', 1)
            if is_valid == False: no_create = False

        if 'password_reg' in data:
            is_valid = cls.validar_largo(data, 'password_reg', 7)
            if is_valid == False: no_create = False

            if 'cpassword_reg' in data:
                if data['password_reg'] != data['cpassword_reg']:
                    flash('la contraseña de confirmacion no concide con la contraseña', 'error')
                    is_valid = False
                if is_valid == False: no_create = False

        if 'email' in data:
            if not REGEX_CORREO_VALIDO.match(data['email']):
                flash('El correo no es válido', 'error')
                is_valid = False

            if is_valid == False: no_create = False

            if cls.validar_existe('email', data['email']):
                flash('el correo ya fue ingresado', 'error')
                is_valid = False

            if is_valid == False: no_create = False


        return no_create



    #relacion uno (1) a muchos
    #Metodo de clase de 1 a muchos = 1 usuario es remitente o destinatario de varios mensajes
    #Este metodo obtiene todos los mensajes enviados y recibidos ara un usuario consultado
    #Se obtinene los datos del usuario consultado...
    #Y luego se le agregan tanto los mensajes enviados como recibidos
    #Ambas propiedas mensajes_enviados y mensajes_recibidos, se alamcenaran...
    #Como una lista de objetos, donde cada objeto es un regitro de mensajes
    @classmethod
    def get_mensajes_de_usuario( cls , dato):

        #Se obtienen los datos del usuario que consultamos
        query = 'SELECT * FROM usuarios where id = %(id)s'
        results = []
        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db( query , dato)

        usuario = cls(results[0])


        #Se obtienen los datos de los mensajes enviados por el usuario que consultamos
        query = 'SELECT m.id, m.cuerpo, CONCAT(u1.nombre, " ", u1.apellido) as autor, CONCAT(u2.nombre, " ", u2.apellido) as destinatario, m.created_at, m.updated_at FROM mensajes m LEFT JOIN usuarios u1 ON m.autor = u1.id left join usuarios u2 on  m.destinatario = u2.id WHERE u1.id = %(id)s'
        results = []
        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db( query , dato)

        #Almacenamos los datos de los mensajes de usuarios en la propiedad 
        if results:
            for row_from_db in results:
                # ahora parseamos los datos de los mensajes para crear instancias de usuarios y agregarlas a nuestra lista

                mensaje_data = {
                    "id" : row_from_db["id"],
                    "cuerpo" : row_from_db["cuerpo"],
                    "autor" : row_from_db["autor"],
                    "destinatario"   : row_from_db["destinatario"],
                    "created_at": row_from_db["created_at"],
                    "updated_at": row_from_db["updated_at"],
                    "tiempo_mensajes_enviados": str(datetime.today()-row_from_db["updated_at"]),
                    "tiempo_mensajes_recibidos": ""
                }

                usuario.mensajes_enviados.append( mensaje.Mensaje( mensaje_data ) )



        query = 'SELECT m.id, m.cuerpo, CONCAT(u1.nombre, " ", u1.apellido) as destinatario, CONCAT(u2.nombre, " ", u2.apellido) as autor, m.created_at, m.updated_at FROM mensajes m LEFT JOIN usuarios u1 ON m.destinatario = u1.id left join usuarios u2 on  m.autor = u2.id WHERE u1.id = %(id)s'
        results = []
        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db( query , dato)

        if results:
            for row_from_db in results:
                # ahora parseamos los datos de los mensajes para crear instancias de usuarios y agregarlas a nuestra lista
                mensaje_data = {
                    "id" : row_from_db["id"],
                    "cuerpo" : row_from_db["cuerpo"],
                    "autor" : row_from_db["autor"],
                    "destinatario"   : row_from_db["destinatario"],
                    "created_at": row_from_db["created_at"],
                    "updated_at": row_from_db["updated_at"],
                    "tiempo_mensajes_enviados": "",
                    "tiempo_mensajes_recibidos": str(datetime.today()-row_from_db["updated_at"])
                }
                usuario.mensajes_recibidos.append(mensaje.Mensaje( mensaje_data ) )

        return usuario