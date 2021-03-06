from flask import _app_ctx_stack, jsonify
import pymysql
from controladores.indexcontroller import Indexcontroller
from controladores.registrocontroller import Registrocontroller
from controladores.principalcontroller import Principalcontroller
from servicios.weblogging import Applogging
from servicios.mysqlDB import MysqlDB
from servicios.autenticacion import Autenticacion
from modelos import usuario
from servicios.clienteRPI import clienteRPI

pymysql.install_as_MySQLdb() # hay un error con el paquete principal de mysqlclient, utilizo esta linea para obligar utilizar este paquete

class Startup:

    def __init__(self, app):
        self.__app = app
        self.__log_startup = Applogging("Startup")
        self.__servicio_db = None
        self.__servicioRPi1 = None
        self.__servicioRPi2 = None
        self.__inyeccion_dependencias()

    def __inyeccion_dependencias(self):
        self.__log_startup.info_log("Iniciando instacias de la aplicacion")
        self.__add_servicio_db()
        self.__add_servicio_autenticacion()
        self.__add_servicio_cliente_rpi1()
        self.__add_servicio_cliente_rpi2()

    def __add_servicio_db(self):
        try: 
            self.__log_startup.info_log("Iniciando servicio mysql...")
            self.__servicio_db = MysqlDB(self.__app, _app_ctx_stack)
            self.sesion = self.__servicio_db.sesion
            self.__log_startup.info_log("Creando tablas")
            usuario.Base.metadata.create_all(bind = self.__servicio_db.engine)
            self.sesion.commit()
            self.sesion.close()
        except:
            self.__log_startup.error_log("Error a la hora de crear tablas")

    def __add_servicio_autenticacion(self):
        self.__log_startup.info_log("Iniciando servicio autenticacion...")
        self.servicio_autenticacion = Autenticacion(self.__servicio_db)

        index_controller_log = Applogging("Controlador Index")
        self.__app.add_url_rule('/', endpoint = 'index', view_func = Indexcontroller.as_view(
            'index', autenticacion = self.servicio_autenticacion, index_controller_log = index_controller_log), methods = ["GET", "POST"])

        registro_controller_log = Applogging("Controlador Registro")
        self.__app.add_url_rule('/registro', endpoint = 'registro', view_func = Registrocontroller.as_view(
            'registro', autenticacion = self.servicio_autenticacion, registro_controller_log = registro_controller_log), methods = ["GET", "POST"])


    """ Aqui se aniade el metodo para cliente RPI1 """
    def __add_servicio_cliente_rpi1(self):
        self.__log_startup.info_log("Iniciando servicio cliente RPi1..")
        nombre_log = "RPI1"
        self.__servicioRPi1 = clienteRPI(nombre_log)

    """ Aqui se aniade el metodo para cliente RPI2 """
    def __add_servicio_cliente_rpi2(self):
        self.__log_startup.info_log("Iniciando servicio cliente RPi2..")
        nombre_log = "RPI2"
        self.__servicioRPi2 = clienteRPI(nombre_log)