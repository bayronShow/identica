from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('subscriptions/', views.manage_subscriptions, name='manage_subscriptions'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('monitor/', views.monitor_dashboard, name='monitor_dashboard'),
    path('access-check/', views.website_access_check, name='website_access_check'),
    path('ldap-test/', views.ldap_test_tool, name='ldap_test_tool'),
    # Тестовые страницы
    path('test/library/', views.test_library_page, name='test_library'),
    path('test/research/', views.test_research_page, name='test_research'),
    path('test/admin/', views.test_admin_page, name='test_admin'),
    path('test/courses/', views.test_courses_page, name='test_courses'),
]