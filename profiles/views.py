from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import StudentProfile, Subscription, Website
from .forms import StudentProfileForm, SubscriptionForm
from .ldap_utils import get_user_accessible_websites, check_website_access

def home(request):
    return render(request, 'profiles/home.html')

@login_required
def profile_view(request):
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        student_profile = StudentProfile.objects.create(user=request.user)
    
    subscriptions = Subscription.objects.filter(
        student=student_profile, 
        is_active=True
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
    
    current_subscriptions = Subscription.objects.filter(
        student=student_profile, 
        is_active=True
    ).values_list('website_id', flat=True)
    
    if request.method == 'POST':
        selected_websites = request.POST.getlist('websites')
        
        with transaction.atomic():
            Subscription.objects.filter(student=student_profile).update(is_active=False)
            
            for website_id in selected_websites:
                website = Website.objects.get(id=website_id)
                subscription, created = Subscription.objects.get_or_create(
                    student=student_profile,
                    website=website,
                    defaults={'is_active': True}
                )
                if not created:
                    subscription.is_active = True
                    subscription.save()
        
        messages.success(request, 'Подписки успешно обновлены!')
        return redirect('profile')
    
    websites_by_category = {}
    for website in Website.objects.filter(is_active=True).select_related('category'):
        category_name = website.category.name
        if category_name not in websites_by_category:
            websites_by_category[category_name] = []
        websites_by_category[category_name].append(website)
    
    return render(request, 'profiles/subscriptions.html', {
        'websites_by_category': websites_by_category,
        'current_subscriptions': list(current_subscriptions),
        'active_tab': 'subscriptions'
    })

@login_required
def dashboard(request):
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        student_profile = StudentProfile.objects.create(user=request.user)
    
    subscriptions = Subscription.objects.filter(
        student=student_profile, 
        is_active=True
    ).select_related('website')
    
    profile_complete = all([
        student_profile.student_id,
        student_profile.faculty,
        student_profile.course,
        student_profile.group
    ])
    
    return render(request, 'profiles/dashboard.html', {
        'profile': student_profile,
        'subscriptions': subscriptions,
        'active_tab': 'dashboard',
        'profile_complete': profile_complete
    })

@login_required
def monitor_dashboard(request):
    """Панель управления для старосты"""
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Профиль студента не найден.')
        return redirect('dashboard')
    
    # Проверяем, является ли пользователь старостой
    if not student_profile.is_monitor:
        messages.error(request, 'У вас нет прав для доступа к панели старосты.')
        return redirect('dashboard')
    
    # Проверяем, что у старосты заполнена группа
    if not student_profile.group:
        messages.error(request, 'Для доступа к панели старосты необходимо указать группу в вашем профиле.')
        return redirect('profile')
    
    # Получаем статистику
    students_in_group = student_profile.get_students_in_group()
    filled_profiles = student_profile.get_filled_profiles()
    completion_percentage = student_profile.get_completion_percentage()
    group_activity = student_profile.get_group_activity()
    group_students = student_profile.get_group_students()
    
    # Статистика по подпискам для каждого студента
    subscription_stats = []
    for student in group_students:
        subscriptions_count = Subscription.objects.filter(student=student, is_active=True).count()
        profile_complete = all([
            student.student_id is not None and student.student_id != '',
            student.faculty is not None and student.faculty != '',
            student.course is not None,
            student.group is not None and student.group != ''
        ])
        subscription_stats.append({
            'student': student,
            'subscriptions_count': subscriptions_count,
            'profile_complete': profile_complete
        })
    
    context = {
        'student_profile': student_profile,
        'students_in_group': students_in_group,
        'filled_profiles': filled_profiles,
        'completion_percentage': completion_percentage,
        'group_activity': group_activity,
        'group_students': group_students,
        'subscription_stats': subscription_stats,
        'active_tab': 'monitor'
    }
    
    return render(request, 'profiles/monitor_dashboard.html', context)

@login_required
def website_access_check(request):
    """Страница проверки доступа к сайтам"""
    accessible_websites = get_user_accessible_websites(request.user.username)
    
    # Проверяем доступ к конкретному сайту если передан URL
    site_url = request.GET.get('url', '')
    specific_access = None
    if site_url:
        specific_access = check_website_access(request.user.username, site_url)
    
    context = {
        'accessible_websites': accessible_websites,
        'specific_access': specific_access,
        'checked_url': site_url,
        'active_tab': 'access_check'
    }
    
    return render(request, 'profiles/website_access.html', context)

@login_required
def ldap_test_tool(request):
    """Инструмент для тестирования LDAP доступа"""
    from .ldap_utils import (
        check_website_access, 
        get_user_accessible_websites, 
        get_user_ldap_info,
        get_user_groups
    )
    
    username = request.user.username
    user_ldap_info = get_user_ldap_info(username)
    user_groups = get_user_groups(username)
    accessible_websites = get_user_accessible_websites(username)
    
    # Проверка конкретного сайта
    test_url = request.GET.get('test_url', '')
    test_result = None
    if test_url:
        test_result = {
            'url': test_url,
            'access_granted': check_website_access(username, test_url),
            'required_groups': [],  # Можно добавить логику для определения требуемых групп
        }
    
    # Популярные сайты для быстрого тестирования
    popular_sites = [
        {'name': 'Библиотека', 'url': 'https://library.university.local'},
        {'name': 'Научный портал', 'url': 'https://research.university.local'},
        {'name': 'Админка', 'url': 'https://admin.university.local'},
        {'name': 'Курсы', 'url': 'https://courses.university.local'},
        {'name': 'Яндекс', 'url': 'https://yandex.ru'},
        {'name': 'Google', 'url': 'https://google.com'},
        {'name': 'GitHub', 'url': 'https://github.com'},
    ]
    
    context = {
        'user_ldap_info': user_ldap_info,
        'user_groups': user_groups,
        'accessible_websites': accessible_websites,
        'test_result': test_result,
        'popular_sites': popular_sites,
        'active_tab': 'ldap_test'
    }
    
    return render(request, 'profiles/ldap_test_tool.html', context)

def test_library_page(request):
    """Тестовая страница библиотеки"""
    from .ldap_utils import check_website_access
    
    # Проверяем доступ через LDAP
    if not request.user.is_authenticated:
        return redirect('login')
    
    has_access = check_website_access(request.user.username, 'https://library.identica.local')
    
    if not has_access:
        return render(request, 'profiles/access_denied.html', {
            'site_name': 'Библиотека университета',
            'required_groups': ['students', 'staff', 'admins']
        })
    
    return render(request, 'profiles/test_pages/library.html')

def test_research_page(request):
    """Тестовая страница научного портала"""
    from .ldap_utils import check_website_access
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    has_access = check_website_access(request.user.username, 'https://research.identica.local')
    
    if not has_access:
        return render(request, 'profiles/access_denied.html', {
            'site_name': 'Научный портал',
            'required_groups': ['staff', 'admins', 'monitors']
        })
    
    return render(request, 'profiles/test_pages/research.html')

def test_admin_page(request):
    """Тестовая страница админки"""
    from .ldap_utils import check_website_access
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    has_access = check_website_access(request.user.username, 'https://admin.identica.local')
    
    if not has_access:
        return render(request, 'profiles/access_denied.html', {
            'site_name': 'Административная панель',
            'required_groups': ['staff', 'admins']
        })
    
    return render(request, 'profiles/test_pages/admin.html')

def test_courses_page(request):
    """Тестовая страница курсов"""
    from .ldap_utils import check_website_access
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    has_access = check_website_access(request.user.username, 'https://courses.identica.local')
    
    if not has_access:
        return render(request, 'profiles/access_denied.html', {
            'site_name': 'Портал курсов',
            'required_groups': ['students', 'staff', 'admins', 'monitors']
        })
    
    return render(request, 'profiles/test_pages/courses.html')