from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__)

from . import views
from . import group
from . import templates
from . import member
