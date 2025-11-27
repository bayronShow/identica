from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from datetime import timedelta
from .models import StudentProfile, WebsiteCategory, Website, Subscription

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'faculty', 'course', 'group', 'view_on_site_link']
    list_filter = ['faculty', 'course']
    search_fields = ['user__username', 'student_id', 'user__first_name', 'user__last_name']
    list_display_links = ['user', 'student_id']
    list_per_page = 20
    
    def view_on_site_link(self, obj):
        return format_html(
            '<a class="admin-btn admin-btn-primary" href="{}" target="_blank">🌐 На сайт</a>',
            reverse('home')
        )
    view_on_site_link.short_description = 'Действия'

@admin.register(WebsiteCategory)
class WebsiteCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'website_count', 'view_on_site_link']
    search_fields = ['name']
    list_per_page = 20
    
    def website_count(self, obj):
        count = obj.website_set.count()
        return format_html('<span class="badge">{}</span>', count)
    website_count.short_description = 'Сайтов'
    
    def view_on_site_link(self, obj):
        return format_html(
            '<a class="admin-btn admin-btn-primary" href="{}" target="_blank">🌐 На сайт</a>',
            reverse('home')
        )
    view_on_site_link.short_description = 'Действия'

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'url_link', 'category', 'subscription_type_badge', 
        'duration_days', 'requires_approval_badge', 'is_active_badge', 
        'view_on_site_link'
    ]
    list_filter = ['category', 'is_active', 'subscription_type', 'requires_approval']
    search_fields = ['name', 'url']
    list_editable = ['duration_days']
    list_per_page = 20
    
    def url_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)
    url_link.short_description = 'URL'
    
    def subscription_type_badge(self, obj):
        if obj.subscription_type == 'auto':
            return format_html('<span class="badge badge-success">🔄 Авто</span>')
        return format_html('<span class="badge badge-warning">👨‍💼 Ручная</span>')
    subscription_type_badge.short_description = 'Тип подписки'
    
    def requires_approval_badge(self, obj):
        if obj.requires_approval:
            return format_html('<span class="badge badge-danger">✅ Требует подтверждения</span>')
        return format_html('<span class="badge badge-success">⚡ Мгновенная</span>')
    requires_approval_badge.short_description = 'Подтверждение'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge badge-success">✅ Активен</span>')
        return format_html('<span class="badge badge-danger">❌ Неактивен</span>')
    is_active_badge.short_description = 'Статус'
    
    def view_on_site_link(self, obj):
        return format_html(
            '<a class="admin-btn admin-btn-primary" href="{}" target="_blank">🌐 На сайт</a>',
            reverse('home')
        )
    view_on_site_link.short_description = 'Действия'

@admin.register(Subscription)  # ← ДОБАВЬТЕ ЭТОТ ДЕКОРАТОР
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'website', 'subscribed_at', 'expires_at', 
        'status_badge', 'days_remaining_display', 'approval_info',
        'quick_actions'
    ]
    list_filter = ['status', 'website', 'subscribed_at']
    search_fields = ['student__user__username', 'website__name']
    readonly_fields = ['subscribed_at', 'approved_at']
    list_per_page = 20
    actions = ['approve_selected_subscriptions', 'reject_selected_subscriptions']  # ← ДОБАВЬТЕ ЭТО
    
    def status_badge(self, obj):
        status_colors = {
            'pending': 'warning',
            'active': 'success',
            'expired': 'secondary',
            'rejected': 'danger'
        }
        status_icons = {
            'pending': '⏳',
            'active': '✅',
            'expired': '⏰',
            'rejected': '❌'
        }
        return format_html(
            '<span class="badge badge-{}">{} {}</span>',
            status_colors.get(obj.status, 'secondary'),
            status_icons.get(obj.status, '❓'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Статус'
    
    def days_remaining_display(self, obj):
        if obj.status == 'active' and obj.days_remaining > 0:
            return format_html('<span class="badge badge-info">{} дн.</span>', obj.days_remaining)
        elif obj.status == 'active' and obj.days_remaining == 0:
            return format_html('<span class="badge badge-warning">Сегодня</span>')
        return '-'
    days_remaining_display.short_description = 'Осталось'
    
    def approval_info(self, obj):
        if obj.approved_by:
            return format_html(
                '<small>{}<br>{}</small>',
                obj.approved_by.username,
                obj.approved_at.strftime('%d.%m.%Y %H:%M') if obj.approved_at else ''
            )
        return '-'
    approval_info.short_description = 'Подтверждено'
    
    def quick_actions(self, obj):
        if obj.status == 'pending':
            return format_html(
                '''
                <div style="display: flex; gap: 5px;">
                    <a href="{}" class="admin-btn admin-btn-success" style="padding: 4px 8px;">✅</a>
                    <a href="{}" class="admin-btn admin-btn-danger" style="padding: 4px 8px;">❌</a>
                </div>
                ''',
                f"subscription/{obj.id}/approve/",
                f"subscription/{obj.id}/reject/"
            )
        return '-'
    quick_actions.short_description = 'Действия'
    
    # ДОБАВЬТЕ ЭТИ МЕТОДЫ ДЛЯ МАССОВЫХ ДЕЙСТВИЙ
    def approve_selected_subscriptions(self, request, queryset):
        updated_count = 0
        for subscription in queryset.filter(status='pending'):
            subscription.status = 'active'
            subscription.approved_by = request.user
            subscription.approved_at = timezone.now()
            
            # Устанавливаем дату истечения если нужно
            if subscription.website.duration_days > 0 and not subscription.expires_at:
                subscription.expires_at = timezone.now() + timedelta(days=subscription.website.duration_days)
            
            subscription.save()
            updated_count += 1
            
        self.message_user(request, f"✅ {updated_count} подписок подтверждено.")
    approve_selected_subscriptions.short_description = "✅ Подтвердить выбранные подписки"
    
    def reject_selected_subscriptions(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"❌ {updated} подписок отклонено.")
    reject_selected_subscriptions.short_description = "❌ Отклонить выбранные подписки"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('subscription/<path:object_id>/approve/', self.admin_site.admin_view(self.approve_subscription)),
            path('subscription/<path:object_id>/reject/', self.admin_site.admin_view(self.reject_subscription)),
        ]
        return custom_urls + urls
    
    def approve_subscription(self, request, object_id):
        subscription = get_object_or_404(Subscription, id=object_id)
        if subscription.status == 'pending':
            subscription.status = 'active'
            subscription.approved_by = request.user
            subscription.approved_at = timezone.now()
            
            # Устанавливаем дату истечения если нужно
            if subscription.website.duration_days > 0 and not subscription.expires_at:
                subscription.expires_at = timezone.now() + timedelta(days=subscription.website.duration_days)
            
            subscription.save()
            self.message_user(request, f"✅ Подписка на '{subscription.website.name}' подтверждена!")
        else:
            self.message_user(request, "❌ Подписка уже обработана.", level='error')
        return redirect('admin:profiles_subscription_changelist')
    
    def reject_subscription(self, request, object_id):
        subscription = get_object_or_404(Subscription, id=object_id)
        if subscription.status == 'pending':
            subscription.status = 'rejected'
            subscription.save()
            self.message_user(request, f"❌ Подписка на '{subscription.website.name}' отклонена.")
        else:
            self.message_user(request, "❌ Подписка уже обработана.", level='error')
        return redirect('admin:profiles_subscription_changelist')

