from django import forms
from .models import StudentProfile, Website, Report, Announcement

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['student_id', 'faculty', 'course', 'group', 'phone', 'birth_date', 'avatar', 'role']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер студенческого билета'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер группы'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер телефона'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'student_id': 'Студенческий билет',
            'faculty': 'Факультет',
            'course': 'Курс',
            'group': 'Группа',
            'phone': 'Телефон',
            'birth_date': 'Дата рождения',
            'avatar': 'Аватар',
            'role': 'Роль в системе',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_id'].required = True
        self.fields['faculty'].required = True
        self.fields['course'].required = True
        self.fields['group'].required = True

class SubscriptionForm(forms.Form):
    websites = forms.ModelMultipleChoiceField(
        queryset=Website.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        required=False,
        label="Выберите сайты для подписки"
    )

# Новые формы для расширенного функционала
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'report_type', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название отчета'}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Название отчета',
            'report_type': 'Тип отчета',
            'is_public': 'Сделать отчет публичным',
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority', 'target', 'target_group', 'target_course']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок объявления'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Текст объявления'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'target': forms.Select(attrs={'class': 'form-control', 'id': 'target-select'}),
            'target_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер группы'}),
            'target_course': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Номер курса', 'min': 1, 'max': 6}),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
            'priority': 'Приоритет',
            'target': 'Целевая аудитория',
            'target_group': 'Группа',
            'target_course': 'Курс',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем поля, которые не нужны для выбранной целевой аудитории
        self.fields['target_group'].required = False
        self.fields['target_course'].required = False

class RoleManagementForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=StudentProfile.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Пользователь"
    )
    new_role = forms.ChoiceField(
        choices=StudentProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Новая роль"
    )

class BulkEmailForm(forms.Form):
    SUBJECT_CHOICES = [
        ('academic', 'Академическая информация'),
        ('events', 'Мероприятия'),
        ('announcements', 'Объявления'),
        ('other', 'Другое'),
    ]
    
    subject_type = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Тема письма"
    )
    custom_subject = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'или введите свою тему'}),
        label="Своя тема"
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Текст сообщения...'}),
        label="Сообщение"
    )
    target_roles = forms.MultipleChoiceField(
        choices=StudentProfile.ROLE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Отправить ролям",
        initial=['student']
    )
    target_course = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
        label="Курс (опционально)"
    )
    target_group = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Группа (опционально)"
    )

class AnalyticsFilterForm(forms.Form):
    PERIOD_CHOICES = [
        ('week', 'Неделя'),
        ('month', 'Месяц'),
        ('quarter', 'Квартал'),
        ('year', 'Год'),
        ('custom', 'Произвольный период'),
    ]
    
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'period-select'}),
        label="Период"
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'start-date'}),
        label="Начальная дата"
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'end-date'}),
        label="Конечная дата"
    )
    report_type = forms.MultipleChoiceField(
        choices=[
            ('subscriptions', 'Подписки'),
            ('activity', 'Активность'),
            ('academic', 'Успеваемость'),
            ('demographic', 'Демография'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Типы отчетов"
    )

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['student_id', 'faculty', 'course', 'group', 'phone', 'birth_date', 'avatar', 'role']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер студенческого билета'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер группы'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер телефона'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'student_id': 'Студенческий билет',
            'faculty': 'Факультет',
            'course': 'Курс',
            'group': 'Группа',
            'phone': 'Телефон',
            'birth_date': 'Дата рождения',
            'avatar': 'Аватар',
            'role': 'Роль в системе',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_id'].required = True
        self.fields['faculty'].required = True
        self.fields['course'].required = True
        self.fields['group'].required = True

class SubscriptionForm(forms.Form):
    websites = forms.ModelMultipleChoiceField(
        queryset=Website.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        required=False,
        label="Выберите сайты для подписки"
    )

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['student_id', 'faculty', 'course', 'group', 'phone', 'birth_date', 'avatar']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер студенческого билета'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер группы'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер телефона'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'student_id': 'Студенческий билет',
            'faculty': 'Факультет',
            'course': 'Курс',
            'group': 'Группа',
            'phone': 'Телефон',
            'birth_date': 'Дата рождения',
            'avatar': 'Аватар',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Скрываем поле роли для обычных пользователей
        if self.user and not self.user.is_staff:
            if 'role' in self.fields:
                del self.fields['role']
        
        self.fields['student_id'].required = True
        self.fields['faculty'].required = True
        self.fields['course'].required = True
        self.fields['group'].required = True

class AdminStudentProfileForm(forms.ModelForm):
    """Форма только для администраторов с возможностью изменения ролей"""
    class Meta:
        model = StudentProfile
        fields = ['student_id', 'faculty', 'course', 'group', 'phone', 'birth_date', 'avatar', 'role']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер студенческого билета'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер группы'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер телефона'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'student_id': 'Студенческий билет',
            'faculty': 'Факультет',
            'course': 'Курс',
            'group': 'Группа',
            'phone': 'Телефон',
            'birth_date': 'Дата рождения',
            'avatar': 'Аватар',
            'role': 'Роль в системе',
        }

class SubscriptionForm(forms.Form):
    websites = forms.ModelMultipleChoiceField(
        queryset=Website.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        required=False,
        label="Выберите сайты для подписки"
    )