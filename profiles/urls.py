from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('subscriptions/', views.manage_subscriptions, name='manage_subscriptions'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('subscription/cancel/<int:subscription_id>/', views.cancel_subscription, name='cancel_subscription'),
    
    # Маршруты для разных ролей
    path('monitor/', views.monitor_dashboard, name='monitor_dashboard'),
    path('curator/', views.curator_dashboard, name='curator_dashboard'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    
    # Дополнительные маршруты для преподавателя
    path('teacher/reports/', views.teacher_reports, name='teacher_reports'),
    path('teacher/analytics/', views.teacher_analytics, name='teacher_analytics'),
    path('teacher/announcements/', views.teacher_announcements, name='teacher_announcements'),
]