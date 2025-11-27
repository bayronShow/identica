from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from profiles.admin_site import custom_admin_site

# Заменяем стандартную админку на кастомную
urlpatterns = [
    path('admin/', custom_admin_site.urls),  # Используем кастомную админку
    path('', include('profiles.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='profiles/login.html'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)