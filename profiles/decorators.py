from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import StudentProfile

def role_required(allowed_roles):
    """
    Декоратор для проверки роли пользователя
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            profile = get_object_or_404(StudentProfile, user=request.user)
            if profile.role not in allowed_roles:
                raise PermissionDenied("У вас недостаточно прав для доступа к этой странице.")
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

def monitor_required(view_func):
    """Только для старост и выше"""
    return role_required(['monitor', 'curator', 'teacher', 'admin'])(view_func)

def curator_required(view_func):
    """Только для кураторов и выше"""
    return role_required(['curator', 'teacher', 'admin'])(view_func)

def teacher_required(view_func):
    """Только для преподавателей и выше"""
    return role_required(['teacher', 'admin'])(view_func)