from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

class StudentProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('monitor', 'Староста'),
        ('curator', 'Куратор'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    ]
    
    FACULTY_CHOICES = [
        ('computer_science', 'Компьютерные науки'),
        ('engineering', 'Инженерия'),
        ('business', 'Бизнес-администрирование'),
        ('arts', 'Искусство и гуманитарные науки'),
        ('science', 'Естественные науки'),
        ('medicine', 'Медицина'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Студенческий билет')
    faculty = models.CharField(max_length=50, choices=FACULTY_CHOICES, null=True, blank=True, verbose_name='Факультет')
    course = models.IntegerField(choices=[(i, f'{i} курс') for i in range(1, 7)], null=True, blank=True, verbose_name='Курс')
    group = models.CharField(max_length=10, null=True, blank=True, verbose_name='Группа')
    phone = models.CharField(max_length=15, blank=True, verbose_name='Телефон')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='student',
        verbose_name='Роль'
    )
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_monitor(self):
        return self.role == 'monitor'
    
    @property
    def is_curator(self):
        return self.role == 'curator'
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    @property
    def is_admin_role(self):
        return self.role == 'admin'
    
    def get_students_in_group(self):
        """Получить студентов в той же группе (для старосты)"""
        if self.is_monitor and self.group:
            return StudentProfile.objects.filter(
                group=self.group,
                role='student'
            )
        return StudentProfile.objects.none()
    
    def get_students_in_course(self):
        """Получить студентов на том же курсе (для куратора)"""
        if self.is_curator and self.course:
            return StudentProfile.objects.filter(
                course=self.course,
                role__in=['student', 'monitor']
            )
        return StudentProfile.objects.none()
    
    def get_all_students(self):
        """Получить всех студентов (для преподавателя)"""
        if self.is_teacher:
            return StudentProfile.objects.filter(
                role__in=['student', 'monitor']
            )
        return StudentProfile.objects.none()

class WebsiteCategory(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория сайта'
        verbose_name_plural = 'Категории сайтов'

class Website(models.Model):
    SUBSCRIPTION_TYPES = [
        ('auto', 'Автоматическая подписка'),
        ('manual', 'Требует подтверждения админа'),
    ]
    
    DURATION_CHOICES = [
        (30, '30 дней'),
        (90, '90 дней'),
        (180, '180 дней'),
        (365, '1 год'),
        (0, 'Бессрочная'),
    ]
    
    ACCESS_CHOICES = [
        ('all', 'Все пользователи'),
        ('students', 'Только студенты'),
        ('monitors', 'Старосты и выше'),
        ('curators', 'Кураторы и выше'),
        ('teachers', 'Преподаватели и выше'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Название')
    url = models.URLField(verbose_name='URL адрес')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(WebsiteCategory, on_delete=models.CASCADE, verbose_name='Категория')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    subscription_type = models.CharField(
        max_length=10, 
        choices=SUBSCRIPTION_TYPES, 
        default='auto',
        verbose_name='Тип подписки'
    )
    duration_days = models.IntegerField(
        choices=DURATION_CHOICES,
        default=30,
        verbose_name='Длительность подписки (дней)'
    )
    requires_approval = models.BooleanField(default=False, verbose_name='Требует подтверждения')
    access_level = models.CharField(
        max_length=10,
        choices=ACCESS_CHOICES,
        default='all',
        verbose_name='Уровень доступа'
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Веб-сайт'
        verbose_name_plural = 'Веб-сайты'
    
    def can_access(self, user_profile):
        """Проверяет, может ли пользователь получить доступ к этому сайту"""
        access_map = {
            'all': True,
            'students': user_profile.role in ['student', 'monitor', 'curator', 'teacher', 'admin'],
            'monitors': user_profile.role in ['monitor', 'curator', 'teacher', 'admin'],
            'curators': user_profile.role in ['curator', 'teacher', 'admin'],
            'teachers': user_profile.role in ['teacher', 'admin'],
        }
        return access_map.get(self.access_level, False)

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('active', 'Активна'),
        ('expired', 'Истекла'),
        ('rejected', 'Отклонена'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, verbose_name='Пользователь')
    website = models.ForeignKey(Website, on_delete=models.CASCADE, verbose_name='Веб-сайт')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')
    expires_at = models.DateTimeField(verbose_name='Истекает', null=True, blank=True)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Статус'
    )
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Подтверждено'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата подтверждения')
    
    class Meta:
        unique_together = ('student', 'website')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
    
    def __str__(self):
        return f"{self.student} - {self.website}"
    
    def save(self, *args, **kwargs):
        if not self.pk and self.website.duration_days > 0:
            self.expires_at = timezone.now() + timedelta(days=self.website.duration_days)
        
        if self.status == 'active' and not self.approved_at:
            self.approved_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False
    
    @property
    def days_remaining(self):
        if self.expires_at and self.status == 'active':
            delta = self.expires_at - timezone.now()
            return max(0, delta.days)
        return 0

# Дополнительные модели для расширенного функционала
class Report(models.Model):
    REPORT_TYPES = [
        ('subscriptions', 'Отчет по подпискам'),
        ('activity', 'Отчет по активности'),
        ('academic', 'Академический отчет'),
        ('custom', 'Пользовательский отчет'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Название отчета')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name='Тип отчета')
    created_by = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, verbose_name='Создатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    data = models.JSONField(default=dict, verbose_name='Данные отчета')
    is_public = models.BooleanField(default=False, verbose_name='Публичный отчет')
    
    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
    
    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"

class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]
    
    TARGET_CHOICES = [
        ('all', 'Все пользователи'),
        ('students', 'Только студенты'),
        ('monitors', 'Старосты'),
        ('curators', 'Кураторы'),
        ('teachers', 'Преподаватели'),
        ('group', 'Конкретная группа'),
        ('course', 'Конкретный курс'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    created_by = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='Приоритет')
    target = models.CharField(max_length=10, choices=TARGET_CHOICES, default='all', verbose_name='Целевая аудитория')
    target_group = models.CharField(max_length=10, blank=True, verbose_name='Группа (если выбрана)')
    target_course = models.IntegerField(null=True, blank=True, verbose_name='Курс (если выбран)')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
    
    def __str__(self):
        return self.title

class AnalyticsData(models.Model):
    """Модель для хранения аналитических данных"""
    data_type = models.CharField(max_length=50, verbose_name='Тип данных')
    period = models.DateField(verbose_name='Период')
    data = models.JSONField(default=dict, verbose_name='Данные')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Аналитические данные'
        verbose_name_plural = 'Аналитические данные'
        unique_together = ('data_type', 'period')
    
    def __str__(self):
        return f"{self.data_type} - {self.period}"

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    if hasattr(instance, 'studentprofile'):
        instance.studentprofile.save()