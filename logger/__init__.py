from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config.from_object('instance.config.Config')
db = SQLAlchemy(app)

from logger.views.search import LogSimpleSearch, LogAdvancedSearch

api.add_resource(LogSimpleSearch, '/search/<string:browser>/<string:country>')
api.add_resource(LogAdvancedSearch, '/advanced-search/')
