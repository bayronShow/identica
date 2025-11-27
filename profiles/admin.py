from django.contrib import admin
from .models import StudentProfile, WebsiteCategory, Website, Subscription

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'faculty', 'course', 'group', 'is_monitor']
    list_filter = ['faculty', 'course', 'is_monitor']
    search_fields = ['user__username', 'student_id']

@admin.register(WebsiteCategory)
class WebsiteCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'url']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['student', 'website', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'website']
    search_fields = ['student__user__username', 'website__name']