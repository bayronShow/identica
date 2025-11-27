from django import forms
from .models import StudentProfile, Website

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