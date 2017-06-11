import base64
from flask import Blueprint
manage = Blueprint('manage',__name__)

from . import views, errors


@manage.app_context_processor
def inject_base64():
    b = base64.b64encode
    str1 = str
    return dict(b=b,str=str1)
