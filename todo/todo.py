from flask import (
    Blueprint, flash, g, render_template, request, url_for, redirect
)
from werkzeug.exceptions import abort
from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todo',__name__)


@bp.route('/')
@login_required
# Esta funcion busca todos los campos que esten relacionados con el id de nuestro usuario
# pero solo si hay una secion iniciada
def index():
    db,c=get_db()
    c.execute(
        'select t.id, t.description, u.username, t.completed, t.created_at'
        ' from todo t JOIN user u on t.created_by = u.id where t.created_by = %s order by created_at desc',
        (g.user['id'],)
    )
    todos = c.fetchall()
    # una vez recopilados los datos de la BD renderisamos index.html y le pasamos nuestos datos a traves de todos
    return render_template('todo/index.html',todos=todos)

    
@bp.route('/create', methods=['GET', 'POST'])
@login_required
# esta funcion creamos las tareas que esten relacionados con el id de nuestro usuario
def create():
    if request.method == 'POST':
        # recuperamos la descripcion del formulario
        description=request.form['description']
        error=None
        # si no hay descripcion devolvemos un error
        if not description:
            error='descripción es requerida'
        if error is not None:
            flash(error)
        else:
            # una vez verificado el campo de descripcion lo insertamos a nuestra base de datos
            db,c=get_db()
            c.execute(
                'insert into todo (description, completed, created_by) values(%s, %s, %s)',
                 (description, False, g.user['id'])
            )
            db.commit()
            # regresamos al inicio
            return redirect(url_for('todo.index'))

    return render_template('todo/create.html')

# Esta funcion busca todos los campos que esten relacionados con el id de nuestro usuario
# es una funcion que usaremos en def update()
def get_todo(id):
    db, c=get_db()
    c.execute(
        'select t.id, t.description, t.completed, t.created_by, t.created_at, u.username '
        'from todo t join user u on t.created_by = u.id where t.id = %s',
        (id,)
    )
    todo=c.fetchone()

    if todo is None:
        abort(404, "El todo de id {0} no existe".format(id))
    return todo

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
# esta funcion actualizara nuestros todos
def update(id):
    # usamos get_todo para obtener los datos del todo a modificar 
    todo=get_todo(id)
    if request.method=='POST':
         # recuperamos la descripcion del formulario
        description=request.form['description']
        # para el checkbox necesitamos hacerlo por separado
        completed= True if request.form.get('completed') == 'on' else False
        error=None
        if not description:
            error="La descripcion es requerida"
        if error is not None:
            flash(error)
        else:
            # actualizamos los datos de la bd
            db,c=get_db()
            c.execute(
            'update todo set description = %s, completed = %s'
            ' where id = %s and created_by = %s', (description,completed,id,g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update.html',todo=todo)

    
@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
# Funcion para eliminar una entrada
def delete(id):
    db,c=get_db()
    c.execute('delete from todo where id = %s and created_by = %s', (id,g.user['id']))
    db.commit()
    return redirect(url_for('todo.index'))