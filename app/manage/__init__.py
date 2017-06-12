import base64
from flask import Blueprint
import time
manage = Blueprint('manage',__name__)

from . import views, errors


@manage.app_context_processor
def inject_base64():
    b = base64.b64encode
    str1 = str
    fmttimestamp = f2t
    return dict(b=b, str=str1, fmttime=fmttimestamp)


def f2t(timestamp):
    x = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', x)
