from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q
import json
from datetime import datetime, timedelta
from .models import StudentProfile, Subscription, Website, Report, Announcement, AnalyticsData
from .forms import StudentProfileForm, ReportForm, AnnouncementForm, RoleManagementForm, BulkEmailForm, AnalyticsFilterForm
from .decorators import monitor_required, curator_required, teacher_required

def home(request):
    return render(request, 'profiles/home.html')

@login_required
def profile_view(request):
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        student_profile = StudentProfile.objects.create(user=request.user)
    
    # Только активные подписки
    subscriptions = Subscription.objects.filter(
        student=student_profile, 
        status='active'
    ).select_related('website')
    
    # Ожидающие подтверждения
    pending_subscriptions = Subscription.objects.filter(
        student=student_profile,
        status='pending'
    ).select_related('website')
    
    if request.method == 'POST':
        form = StudentProfileForm(
            request.POST, 
            request.FILES, 
            instance=student_profile
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = StudentProfileForm(instance=student_profile)
    
    profile_complete = all([
        student_profile.student_id,
        student_profile.faculty,
        student_profile.course,
        student_profile.group
    ])
    
    return render(request, 'profiles/profile.html', {
        'profile': student_profile,
        'form': form,
        'subscriptions': subscriptions,
        'pending_subscriptions': pending_subscriptions,
        'active_tab': 'profile',
        'profile_complete': profile_complete
    })

@login_required
def manage_subscriptions(request):
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        student_profile = StudentProfile.objects.create(user=request.user)
    
    if not all([student_profile.student_id, student_profile.faculty, student_profile.course, student_profile.group]):
        messages.warning(request, 'Пожалуйста, заполните ваш профиль перед управлением подписками.')
        return redirect('profile')
    
    # Получаем только те сайты, к которым пользователь имеет доступ
    available_websites = Website.objects.filter(is_active=True).select_related('category')
    accessible_websites = [w for w in available_websites if w.can_access(student_profile)]
    
    # Получаем текущие подписки пользователя
    current_subscriptions = Subscription.objects.filter(
        student=student_profile
    ).values_list('website_id', flat=True)
    
    # Активные подписки
    subscriptions_active = Subscription.objects.filter(
        student=student_profile,
        status='active'
    ).select_related('website')
    
    # Ожидающие подтверждения
    subscriptions_pending = Subscription.objects.filter(
        student=student_profile,
        status='pending'
    ).select_related('website')
    
    if request.method == 'POST':
        selected_websites = request.POST.getlist('websites')
        
        with transaction.atomic():
            # Удаляем отмененные подписки
            removed_subscriptions = Subscription.objects.filter(
                student=student_profile
            ).exclude(website_id__in=selected_websites)
            removed_count = removed_subscriptions.count()
            removed_subscriptions.delete()
            
            # Добавляем новые подписки
            added_count = 0
            pending_count = 0
            
            for website_id in selected_websites:
                website = Website.objects.get(id=website_id)
                
                # Проверяем доступ
                if not website.can_access(student_profile):
                    messages.error(request, f'У вас нет доступа к сайту "{website.name}"')
                    continue
                
                # Проверяем, нет ли уже подписки
                subscription, created = Subscription.objects.get_or_create(
                    student=student_profile,
                    website=website
                )
                
                if created:
                    # Устанавливаем статус в зависимости от типа подписки
                    if website.requires_approval:
                        subscription.status = 'pending'
                        pending_count += 1
                        messages.info(request, f'Запрос на подписку "{website.name}" отправлен на подтверждение.')
                    else:
                        subscription.status = 'active'
                        added_count += 1
                        messages.success(request, f'✅ Подписка на "{website.name}" активирована!')
                    
                    subscription.save()
            
            if added_count > 0 or removed_count > 0 or pending_count > 0:
                success_msg = f'Подписки обновлены: '
                parts = []
                if added_count > 0:
                    parts.append(f'добавлено {added_count}')
                if pending_count > 0:
                    parts.append(f'ожидают подтверждения {pending_count}')
                if removed_count > 0:
                    parts.append(f'удалено {removed_count}')
                
                messages.success(request, success_msg + ', '.join(parts) + '.')
        
        return redirect('manage_subscriptions')
    
    # Группируем доступные сайты по категориям
    websites_by_category = {}
    for website in accessible_websites:
        category_name = website.category.name
        if category_name not in websites_by_category:
            websites_by_category[category_name] = []
        websites_by_category[category_name].append(website)
    
    return render(request, 'profiles/subscriptions.html', {
        'websites_by_category': websites_by_category,
        'current_subscriptions': list(current_subscriptions),
        'subscriptions_active': subscriptions_active,
        'subscriptions_pending': subscriptions_pending,
        'websites_available': len(accessible_websites),
        'active_tab': 'subscriptions'
    })

@login_required
def dashboard(request):
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        student_profile = StudentProfile.objects.create(user=request.user)
    
    # Активные подписки
    subscriptions = Subscription.objects.filter(
        student=student_profile, 
        status='active'
    ).select_related('website')
    
    # Ожидающие подтверждения
    pending_subscriptions = Subscription.objects.filter(
        student=student_profile,
        status='pending'
    ).select_related('website')
    
    # Проверяем истекшие подписки
    expired_count = Subscription.objects.filter(
        student=student_profile,
        status='active',
        expires_at__lt=timezone.now()
    ).update(status='expired')
    
    profile_complete = all([
        student_profile.student_id,
        student_profile.faculty,
        student_profile.course,
        student_profile.group
    ])
    
    return render(request, 'profiles/dashboard.html', {
        'profile': student_profile,
        'subscriptions': subscriptions,
        'pending_subscriptions': pending_subscriptions,
        'active_tab': 'dashboard',
        'profile_complete': profile_complete
    })

# Новые представления для разных ролей
@login_required
@monitor_required
def monitor_dashboard(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    students_in_group = profile.get_students_in_group()
    
    # Статистика для старосты
    group_stats = {
        'total_students': students_in_group.count(),
        'active_subscriptions': Subscription.objects.filter(
            student__in=students_in_group,
            status='active'
        ).count(),
        'pending_subscriptions': Subscription.objects.filter(
            student__in=students_in_group,
            status='pending'
        ).count(),
        'completed_profiles': students_in_group.filter(
            Q(student_id__isnull=False) & 
            Q(faculty__isnull=False) & 
            Q(course__isnull=False) & 
            Q(group__isnull=False)
        ).count(),
    }
    
    # Последние активности в группе
    recent_announcements = Announcement.objects.filter(
        Q(target='all') | Q(target='students') | Q(target='group', target_group=profile.group),
        is_active=True
    ).order_by('-created_at')[:5]
    
    return render(request, 'profiles/monitor_dashboard.html', {
        'profile': profile,
        'students': students_in_group,
        'group_stats': group_stats,
        'recent_announcements': recent_announcements,
        'active_tab': 'monitor'
    })

@login_required
@curator_required
def curator_dashboard(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    students_in_course = profile.get_students_in_course()
    
    # Статистика для куратора
    course_stats = {
        'total_students': students_in_course.count(),
        'groups_count': students_in_course.values('group').distinct().count(),
        'active_monitors': students_in_course.filter(role='monitor').count(),
    }
    
    # Форма для создания объявлений
    announcement_form = AnnouncementForm()
    
    if request.method == 'POST' and 'create_announcement' in request.POST:
        announcement_form = AnnouncementForm(request.POST)
        if announcement_form.is_valid():
            announcement = announcement_form.save(commit=False)
            announcement.created_by = profile
            announcement.save()
            messages.success(request, 'Объявление успешно создано!')
            return redirect('curator_dashboard')
    
    # Управление ролями в курсе
    role_form = RoleManagementForm()
    role_form.fields['user'].queryset = students_in_course
    
    if request.method == 'POST' and 'change_role' in request.POST:
        role_form = RoleManagementForm(request.POST)
        if role_form.is_valid():
            student_profile = role_form.cleaned_data['user']
            new_role = role_form.cleaned_data['new_role']
            old_role = student_profile.role
            student_profile.role = new_role
            student_profile.save()
            messages.success(request, f'Роль {student_profile.user.username} изменена с {old_role} на {new_role}')
            return redirect('curator_dashboard')
    
    return render(request, 'profiles/curator_dashboard.html', {
        'profile': profile,
        'students': students_in_course,
        'course_stats': course_stats,
        'announcement_form': announcement_form,
        'role_form': role_form,
        'active_tab': 'curator'
    })

@login_required
@teacher_required
def teacher_dashboard(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    all_students = profile.get_all_students()
    
    # Формы для преподавателя
    report_form = ReportForm()
    analytics_form = AnalyticsFilterForm()
    bulk_email_form = BulkEmailForm()
    
    # Статистика для преподавателя
    teacher_stats = {
        'total_students': all_students.count(),
        'total_groups': all_students.values('group').distinct().count(),
        'total_courses': all_students.values('course').distinct().count(),
        'active_subscriptions': Subscription.objects.filter(
            student__in=all_students,
            status='active'
        ).count(),
    }
    
    # Генерация отчетов
    if request.method == 'POST' and 'generate_report' in request.POST:
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.created_by = profile
            
            # Генерация данных отчета в зависимости от типа
            report_type = report_form.cleaned_data['report_type']
            report_data = generate_report_data(report_type, all_students)
            report.data = report_data
            
            report.save()
            messages.success(request, f'Отчет "{report.title}" успешно создан!')
            return redirect('teacher_reports')
    
    # Массовая рассылка email
    if request.method == 'POST' and 'send_bulk_email' in request.POST:
        bulk_email_form = BulkEmailForm(request.POST)
        if bulk_email_form.is_valid():
            # Здесь будет логика отправки email
            messages.info(request, 'Функция массовой рассылки находится в разработке')
            return redirect('teacher_dashboard')
    
    # Аналитика
    if request.method == 'POST' and 'generate_analytics' in request.POST:
        analytics_form = AnalyticsFilterForm(request.POST)
        if analytics_form.is_valid():
            analytics_data = generate_analytics_data(analytics_form.cleaned_data, all_students)
            return render(request, 'profiles/teacher_dashboard.html', {
                'profile': profile,
                'students': all_students,
                'teacher_stats': teacher_stats,
                'report_form': report_form,
                'analytics_form': analytics_form,
                'bulk_email_form': bulk_email_form,
                'analytics_data': analytics_data,
                'active_tab': 'teacher'
            })
    
    return render(request, 'profiles/teacher_dashboard.html', {
        'profile': profile,
        'students': all_students,
        'teacher_stats': teacher_stats,
        'report_form': report_form,
        'analytics_form': analytics_form,
        'bulk_email_form': bulk_email_form,
        'active_tab': 'teacher'
    })

# Дополнительные представления для преподавателя
@login_required
@teacher_required
def teacher_reports(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    reports = Report.objects.filter(created_by=profile).order_by('-created_at')
    
    return render(request, 'profiles/teacher_reports.html', {
        'profile': profile,
        'reports': reports,
        'active_tab': 'teacher_reports'
    })

@login_required
@teacher_required
def teacher_analytics(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    analytics_form = AnalyticsFilterForm()
    
    if request.method == 'POST':
        analytics_form = AnalyticsFilterForm(request.POST)
        if analytics_form.is_valid():
            all_students = profile.get_all_students()
            analytics_data = generate_analytics_data(analytics_form.cleaned_data, all_students)
            
            return render(request, 'profiles/teacher_analytics.html', {
                'profile': profile,
                'analytics_form': analytics_form,
                'analytics_data': analytics_data,
                'active_tab': 'teacher_analytics'
            })
    
    return render(request, 'profiles/teacher_analytics.html', {
        'profile': profile,
        'analytics_form': analytics_form,
        'active_tab': 'teacher_analytics'
    })

@login_required
@teacher_required
def teacher_announcements(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    announcements = Announcement.objects.filter(created_by=profile).order_by('-created_at')
    announcement_form = AnnouncementForm()
    
    if request.method == 'POST':
        announcement_form = AnnouncementForm(request.POST)
        if announcement_form.is_valid():
            announcement = announcement_form.save(commit=False)
            announcement.created_by = profile
            announcement.save()
            messages.success(request, 'Объявление успешно создано!')
            return redirect('teacher_announcements')
    
    return render(request, 'profiles/teacher_announcements.html', {
        'profile': profile,
        'announcements': announcements,
        'announcement_form': announcement_form,
        'active_tab': 'teacher_announcements'
    })

# Вспомогательные функции
def generate_report_data(report_type, students_queryset):
    """Генерация данных для отчета"""
    if report_type == 'subscriptions':
        return {
            'total_subscriptions': Subscription.objects.filter(student__in=students_queryset).count(),
            'active_subscriptions': Subscription.objects.filter(student__in=students_queryset, status='active').count(),
            'popular_websites': list(Website.objects.annotate(
                sub_count=Count('subscription', filter=Q(subscription__student__in=students_queryset))
            ).filter(sub_count__gt=0).order_by('-sub_count').values('name', 'sub_count')[:10]),
            'subscriptions_by_faculty': list(students_queryset.values('faculty').annotate(
                count=Count('subscription', filter=Q(subscription__status='active'))
            )),
        }
    elif report_type == 'activity':
        return {
            'recent_activity': list(Subscription.objects.filter(
                student__in=students_queryset
            ).select_related('student', 'website').order_by('-subscribed_at')[:20].values(
                'student__user__username', 'website__name', 'subscribed_at'
            )),
        }
    return {}

def generate_analytics_data(form_data, students_queryset):
    """Генерация аналитических данных"""
    period = form_data.get('period')
    report_types = form_data.get('report_type', [])
    
    analytics_data = {}
    
    if 'subscriptions' in report_types:
        analytics_data['subscriptions'] = {
            'total': Subscription.objects.filter(student__in=students_queryset).count(),
            'active': Subscription.objects.filter(student__in=students_queryset, status='active').count(),
            'pending': Subscription.objects.filter(student__in=students_queryset, status='pending').count(),
            'by_faculty': list(students_queryset.values('faculty').annotate(
                count=Count('subscription')
            )),
        }
    
    if 'activity' in report_types:
        analytics_data['activity'] = {
            'recent_subscriptions': Subscription.objects.filter(
                student__in=students_queryset,
                subscribed_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }
    
    return analytics_data

@login_required
def cancel_subscription(request, subscription_id):
    try:
        subscription = Subscription.objects.get(
            id=subscription_id,
            student__user=request.user
        )
        website_name = subscription.website.name
        subscription.delete()
        messages.success(request, f'Подписка на {website_name} отменена.')
    except Subscription.DoesNotExist:
        messages.error(request, 'Подписка не найдена.')
    
    return redirect('profile')