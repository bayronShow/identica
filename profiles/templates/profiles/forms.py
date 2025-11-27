class ReportForm(forms.Form):
    REPORT_TYPES = [
        ('subscriptions', 'Отчет по подпискам'),
        ('students', 'Отчет по студентам'),
        ('activity', 'Отчет по активности'),
        ('roles', 'Отчет по распределению ролей'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        label='Тип отчета',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        label='Начальная дата',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    end_date = forms.DateField(
        label='Конечная дата', 
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

class RoleManagementForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Пользователь',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    new_role = forms.ChoiceField(
        choices=StudentProfile.ROLE_CHOICES,
        label='Новая роль',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class BulkEmailForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        label='Тема письма',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    message = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    
    target_roles = forms.MultipleChoiceField(
        choices=StudentProfile.ROLE_CHOICES,
        label='Роли получателей',
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    target_groups = forms.CharField(
        max_length=100,
        required=False,
        label='Группы (через запятую)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ИТ-101, ИТ-102'})
    )