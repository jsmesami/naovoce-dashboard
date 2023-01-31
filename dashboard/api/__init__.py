from flask import Blueprint
from flask_restful import Api

from . import resources

api = Blueprint("api", __name__)
API = Api(api)


API.add_resource(resources.TopUsers, "/creators/top")
