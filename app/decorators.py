from functools import wraps
from flask import abort
from flask_login import current_user
from .permission import UserPermission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(UserPermission.ADMINISTER)(f)


def own_required(group):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if group.owner != current_user:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator