__author__ = 'Omar Galarraga'
__email__ = 'omar.galarraga@polesante.eu'
__version__ = '0.1'

from flask import Flask
from flask_caching import Cache
import os

cache = Cache()

def create_app():
    #config = {
    #    "DEBUG": True,          # some Flask specific configs
    #    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    #    "CACHE_DEFAULT_TIMEOUT": 300
    #}
    app = Flask(__name__, template_folder='.')
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    cache.init_app(app)
    #print('cache initialized')
    # tell Flask to use the above defined config
    #app.config.from_mapping(config)
    #cache = Cache(app)    
    
    #app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    #app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
    app.config['SECRET_KEY'] = 'devkey'
    #cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    #with app.app_context():
    #    cache.init_app(app)

    cache.set('conditions_open_long', "")   
    cache.set('conditions_open_short', "")
    cache.set('conditions_close_long', "")
    cache.set('conditions_close_short', "")
    cache.set('indicators', [])
    cache.set('strategy', None)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import stcreator
    app.register_blueprint(stcreator.bp)

    return app

#@app.before_first_request
#def init_cache():
#    with app.app_context():
#        cache.init_app(app)