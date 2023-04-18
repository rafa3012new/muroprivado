import os
from flask import redirect, render_template, request, flash, session, url_for
from flask_dojo_wall import app
from flask_bcrypt import Bcrypt
from flask_dojo_wall.models.usuario import Usuario
from flask_dojo_wall.models.mensaje import Mensaje
from flask_dojo_wall.config.myfunctions import diferencia_tiempo
from datetime import datetime
import socket   



bcrypt = Bcrypt(app)


@app.route("/")
def index():

    if 'usuario' not in session:
        flash('Primero tienes que logearte', 'error')
        return redirect('/login')

    nombre_sistema = os.environ.get("NOMBRE_SISTEMA")

    datos_usuario = []
    datos_mensaje = []

    if 'idusuario' in session:
        data = {'id': session['idusuario']}
        datos_usuario = Usuario.get_mensajes_de_usuario(data)
        datos_otros_usuarios = Usuario.get_usuarios_enviar(data)

    return render_template("index.html", sistema=nombre_sistema, datos_usuario=datos_usuario, datos_otros_usuarios=datos_otros_usuarios)

@app.route("/login")
def login():

    if 'usuario' in session:
        flash('Ya estás LOGEADO!', 'warning')
        return redirect('/')

    return render_template("login.html")

@app.route("/procesar_registro", methods=["POST"])
def procesar_registro():

    #validaciones del objeto usuario
    if not Usuario.validar(request.form):
        return redirect('/login')


    pass_hash = bcrypt.generate_password_hash(request.form['password_reg'])

    data = {
        'usuario' : request.form['user'],
        'nombre' : request.form['name'],
        'apellido' : request.form['lastname'],
        'email' : request.form['email'],
        'password' : pass_hash,
    }

    resultado = Usuario.save(data)

    if not resultado:
        flash("error al crear el usuario", "error")
        return redirect("/login")

    flash("Usuario creado correctamente", "success")
    return redirect("/login")


@app.route("/procesar_login", methods=["POST"])
def procesar_login():

    usuario = Usuario.buscar(request.form['identification'])

    if not usuario:
        flash("Usuario/Correo/Clave Invalidas", "error")
        return redirect("/login")

    if not bcrypt.check_password_hash(usuario.password, request.form['password']):
        flash("Usuario/Correo/Clave Invalidas", "error")
        return redirect("/login")

    session['idusuario'] = usuario.id
    session['usuario'] = usuario.nombre + " " + usuario.apellido


    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route("/procesar_mensaje", methods=["POST"])
def procesar_mensaje():

    data ={
            'autor':session['idusuario'],
            'destinatario':request.form['idusuario'],
            'cuerpo':request.form['cuerpo']
           }

    try:
        Mensaje.save(data)
        print("mensaje guardado con exito",flush=True)
    except Exception as error:
        print("error al guardar el mensaje enviado",flush=True)

    return redirect('/')


@app.route("/eliminar_mensaje_enviado", methods=["POST"])
def eliminar_mensaje_enviado():

    try:
        Mensaje.delete(request.form['id'])
        print(f"prueba con eliminacion de mensaje con exito {request.form['id']}",flush=True)
    except Exception as error:
        print("error al eliminar el mensaje enviado",flush=True)

    return redirect('/')


@app.route("/eliminar_mensaje_recibido", methods=["POST"])
def eliminar_mensaje_recibido():

    try:
        hostname=socket.gethostname()
        ipaddr=socket.gethostbyname(hostname)
        print("Your Computer Name is:"+hostname)
        print("Your Computer IP Address is:"+ipaddr)

        print(f"prueba con eliminacion de mensaje con exito {request.form['id']}",flush=True)
    except Exception as error:
        print("error al obtener la ip del dispositivo",flush=True)

    return redirect(url_for('danger',ipaddr=ipaddr, msgid=request.form['id']))

@app.route("/danger/<ipaddr>/<msgid>")
def danger(ipaddr,msgid):
    return render_template('danger.html',ipaddr=ipaddr, msgid=msgid)

