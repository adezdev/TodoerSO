import os # el modulo nos permite acceder a a ciertas cosas del sistema operativo
from flask import Flask # importamos el framework

# nos va a servir para inicializar una instancia de nuestra aplicacion
def create_app():
    app=Flask(__name__) # todas las aplicaciones que creamos son una instancia de la clase flask

    # utilizamos las variable de entorno para poder configurar la aplicacion
    # from_mapping nos permite a nosotros definir variables de configuracion que luego nosotros vamos a utilizar
    app.config.from_mapping(
        SECRET_KEY='mikey', # define las sesiones 
        DATABASE_HOST=os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PASSWORD=os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE_USER=os.environ.get('FLASK_DATABASE_USER'),
        DATABASE=os.environ.get('FLASK_DATABASE')
    )
    
    # registro de blueprints
    from.import db 
    db.init_app(app)
    
    from.import auth
    from.import todo

    app.register_blueprint(auth.bp)
    app.register_blueprint(todo.bp)

    return app        