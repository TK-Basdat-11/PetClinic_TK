from functools import wraps
from django.shortcuts import redirect

def role_required(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = request.session.get('user_role')
            
            if not user_role or user_role not in allowed_roles:
                if user_role == 'dokter':
                    return redirect('dashboard:dashboard_dokter')
                elif user_role == 'perawat':
                    return redirect('dashboard:dashboard_perawat')
                elif user_role == 'klien':
                    return redirect('dashboard:dashboard_klien')
                elif user_role == 'fdo':
                    return redirect('dashboard:dashboard_fdo')
                else:
                    # gada rolenya
                    return redirect('authentication:login')
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator 