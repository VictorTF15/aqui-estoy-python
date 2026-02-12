from functools import wraps
from django.shortcuts import redirect

def session_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.session.get('user_id'):
            return view_func(request, *args, **kwargs)
        return redirect('members:login')
    return _wrapped

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            role = request.session.get('user_role')
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)
            # Opcional: redirigir a "no autorizado" si existe
            return redirect('members:lista_casos')
        return _wrapped
    return decorator