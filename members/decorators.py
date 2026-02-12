from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def login_required_session(view_func):
    """
    Decorador que requiere que el usuario esté autenticado mediante sesión.
    Redirige a login si no hay sesión activa.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('members:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    """
    Decorador que requiere que el usuario tenga uno de los roles especificados.
    Uso: @role_required('Administrador', 'Donador')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.session.get('user_id'):
                messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
                return redirect('members:login')
            
            user_role = request.session.get('user_role', '')
            if user_role not in roles:
                messages.error(request, f"No tienes permisos para acceder a esta página. Se requiere rol: {', '.join(roles)}")
                return redirect('members:feed')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def anonymous_required(view_func):
    """
    Decorador que solo permite acceso a usuarios NO autenticados.
    Útil para páginas de login y registro.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_id'):
            messages.info(request, "Ya tienes una sesión activa.")
            return redirect('members:feed')
        return view_func(request, *args, **kwargs)
    return wrapper