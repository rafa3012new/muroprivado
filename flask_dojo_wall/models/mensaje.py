import os
from flask import flash
from flask_dojo_wall.config.mysqlconnection import connectToMySQL
from flask_dojo_wall.models import modelo_base
from flask_dojo_wall.models import usuario
from flask_dojo_wall.utils.regex import REGEX_CORREO_VALIDO
from datetime import datetime


class Mensaje(modelo_base.ModeloBase):

    modelo = 'mensajes'
    campos = ['autor', 'destinatario','cuerpo']

    def __init__(self, data):
        self.id = data['id']
        self.autor = data['autor']
        self.destinatario = data['destinatario']
        self.cuerpo = data['cuerpo']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.tiempo_mensajes_enviados = data["tiempo_mensajes_enviados"]
        self.tiempo_mensajes_recibidos = data['tiempo_mensajes_recibidos']


    @classmethod
    def buscar(cls, dato):
        query = "select * from mensajes where id = %(dato)s"
        data = { 'dato' : dato }
        results = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)

        if len(results) < 1:
            return False
        return cls(results[0])


    @classmethod
    def update(cls,data):
        query = """UPDATE mensajes
                        SET autor = %(nombre)s,
                        SET destinatario = %(apellido)s,
                        SET cuerpo = %(email)s,
                        updated_at=NOW()
                    WHERE id = %(id)s"""
        resultado = connectToMySQL(os.environ.get("BASEDATOS_NOMBRE")).query_db(query, data)
        print("RESULTADO: ", resultado,flush=True)
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

        if 'mesaje' in data:
            is_valid = cls.validar_largo(data, 'name', 5)
            if is_valid == False: no_create = False

        return no_create


