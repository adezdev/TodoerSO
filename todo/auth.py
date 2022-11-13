# este es un blueprint o un conjunto de modulos

import functools #herramientas utiles

#flash permite enviar mensajes genericos a nuestras plantillas
from flask import (
    Blueprint, flash, g, render_template, request, url_for, session, redirect
)
#check_password nos dice si las contraseñas son iguales
#generate_password encripta una contraseña
from werkzeug.security import check_password_hash, generate_password_hash
from todo.db import get_db

#generamos un blueprint que tendra toda la parte de autenticacion
bp=Blueprint('auth',__name__, url_prefix='/auth')

#nuestra primera ruta sera la de registrar
@bp.route('/register',methods=['GET','POST'])
def register():
    # si el metodo es post obtendremos el username y el password ingresados
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        db,c = get_db()
        error=None
        # comprobamos que el username no se repita
        c.execute(
            'select id from user where username = %s', (username,)
        )
        # de ser necesario mandamos un error segun sea el caso
        if not username:
            error = 'Username es requerido'
        if not password:
            error = 'Password es requerido'
        elif c.fetchone() is not None:
            error = 'Usuario {} se encuentra registrado.'.format(username)

        # si no hay ningun error introducimos los valores a la BD encriptando la contraseña previamente
        if error is None:
            c.execute(
                'insert into user (username, password) values(%s,%s)',
                (username, generate_password_hash(password)) 
                )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)
        
    # si el metodo es GET entonces retornaremos este template
    return render_template('auth/register.html')

# la siguiente ruta realizara los procesos de  login
@bp.route('/login', methods=['GET','POST'])
def login():

    # si el metodo es post obtendremos el usuario y contraseña introducidas
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        db,c = get_db()
        error=None
        # buscamos si el username coincide con la base de datos
        c.execute(
            'select * from user where username = %s', (username,)
        )  
        user = c.fetchone()

        # mandamos un mensaje de error segun sea el caso
        if user is None:
            error = 'Username y/o contraseña inválida'

        elif not check_password_hash(user['password'],password):
            error='Username y/o contraseña inválida'
 
        if error is None:
            session.clear()
            session['user_id']=user['id']
            return redirect(url_for('todo.index'))

        flash(error)
    # si el metodo recibido es GET renderizamos login 
    return render_template('auth/login.html')

@bp.before_app_request
def load_loagged_in_user():
    user_id=session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db,c=get_db()
        c.execute(
            'select * from user where id = %s', (user_id,)
        )
        g.user=c.fetchone()


# funcion decoradora para saber si hay un usuario actualmente
def login_required(view):
    @functools.wraps(view)
    def wrapped_view (**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@bp.route('/about')
def about():
    return render_template('todo/acerca.html')
    