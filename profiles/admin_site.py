from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import StudentProfile, WebsiteCategory, Website, Subscription

class CustomAdminSite(AdminSite):
    site_header = "🌿 Identica - Администрирование"
    site_title = "Identica Admin"
    index_title = "⭕ Панель управления Identica"
    
    def get_app_list(self, request):
        """
        Переопределяем порядок приложений в админке
        """
        app_list = super().get_app_list(request)
        
        # Реорганизуем порядок приложений
        reordered_app_list = []
        
        for app in app_list:
            if app['app_label'] == 'profiles':
                reordered_app_list.insert(0, app)  # Профили первыми
            elif app['app_label'] == 'auth':
                reordered_app_list.append(app)  # Аутентификация последней
            else:
                reordered_app_list.append(app)
                
        return reordered_app_list

# Создаем экземпляр кастомной админки
custom_admin_site = CustomAdminSite(name='custom_admin')

# Регистрируем модели в кастомной админке
from .admin import StudentProfileAdmin, WebsiteCategoryAdmin, WebsiteAdmin, SubscriptionAdmin

custom_admin_site.register(StudentProfile, StudentProfileAdmin)
custom_admin_site.register(WebsiteCategory, WebsiteCategoryAdmin)
custom_admin_site.register(Website, WebsiteAdmin)
custom_admin_site.register(Subscription, SubscriptionAdmin)

# Также регистрируем стандартные модели если нужно
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(User, UserAdmin)