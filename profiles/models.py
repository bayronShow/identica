from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class StudentProfile(models.Model):
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
    is_monitor = models.BooleanField(default=False, verbose_name='Староста')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"
    
    class Meta:
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'

class WebsiteCategory(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория сайта'
        verbose_name_plural = 'Категории сайтов'

class Website(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    url = models.URLField(verbose_name='URL адрес')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(WebsiteCategory, on_delete=models.CASCADE, verbose_name='Категория')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Веб-сайт'
        verbose_name_plural = 'Веб-сайты'

class Subscription(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, verbose_name='Студент')
    website = models.ForeignKey(Website, on_delete=models.CASCADE, verbose_name='Веб-сайт')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    
    class Meta:
        unique_together = ('student', 'website')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
    
    def __str__(self):
        return f"{self.student} - {self.website}"

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    if hasattr(instance, 'studentprofile'):
        instance.studentprofile.save()