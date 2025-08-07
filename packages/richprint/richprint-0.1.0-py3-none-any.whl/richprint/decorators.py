from functools import wraps
from richprint import print_status

def log_action(msg):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            print_status(msg)
            return fn(*args, **kwargs)
        return wrapper
    return decorator