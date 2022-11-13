import mysql.connector
import click # herramienta que nos permite ejecotar comandos en la terminal
from flask import current_app, g 
#current_app mantiene la aplicacion que estamos ejecutando 
# g es una variable a la que le podemos asignar distintas variablas y luego acceder a ellas

from flask.cli import with_appcontext
 # with_appcontext nos va a servir para acceder a las variables que se encuentran en las configuraciones de la aplicacion

from .schema import instructions
# importamos un archivo, que contenga todos los scripts para poder crear nuestra BD

# funcion para obtener la base de datos y tambien el cursor dentro de la app
def get_db():
    # si no se encuentra el atributo db dentro de g
    if 'db' not in g:
        # creamos una nueva propieda dentro de g para conectar la bd
        g.db=mysql.connector.connect(
            host=current_app.config['DATABASE_HOST'],
            user=current_app.config['DATABASE_USER'],
            password=current_app.config['DATABASE_PASSWORD'],
            database=current_app.config['DATABASE'],
        )
        # creamos una nueva propieda dentro de g pa acceder a cursor y ejecutar nuestras consultas
        g.c=g.db.cursor(dictionary=True)
    return g.db, g.c

# Funcion para poder cerrar la base de datos cada vez que hagamos una consulta sql
def close_db(e=None):
    db=g.pop('db',None) # de esta manera le quitamos la propiedad de db a g

    #si db esta definido entonces cerramos la conexion de la base de datos
    if db is not None:
        db.close()

# escribir el script necesario para poder ejecutar una instrucciones en sql
def init_db():
    db,c = get_db()

    for i in instructions:
        c.execute(i)
        
    db.commit()

@click.command('init-db')
@with_appcontext

def init_db_command():
    init_db()
    click.echo('Base de datos inicializada') # indica que nuestro script ha terminado de correr con exito

# funcion para indicarle a flask para ejecutar close_db al terminar una peticion
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    