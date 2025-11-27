from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profiles.models import StudentProfile

class Command(BaseCommand):
    help = 'Создает тестовых пользователей для LDAP тестирования'

    def handle(self, *args, **options):
        # Тестовые пользователи
        test_users = [
            {
                'username': 'student1',
                'password': 'password123',
                'email': 'student1@university.local',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'student_id': 'ST001',
                'faculty': 'computer_science',
                'course': 2,
                'group': 'CS-201',
                'is_monitor': False
            },
            {
                'username': 'student2',
                'password': 'password123',
                'email': 'student2@university.local',
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'student_id': 'ST002',
                'faculty': 'engineering',
                'course': 3,
                'group': 'ENG-301',
                'is_monitor': False
            },
            {
                'username': 'monitor1',
                'password': 'password123',
                'email': 'monitor1@university.local',
                'first_name': 'Алексей',
                'last_name': 'Иванов',
                'student_id': 'ST003',
                'faculty': 'computer_science',
                'course': 3,
                'group': 'CS-301',
                'is_monitor': True
            },
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@university.local',
                'first_name': 'Администратор',
                'last_name': 'Системы',
                'student_id': 'ADM001',
                'faculty': 'computer_science',
                'course': 5,
                'group': 'ADMIN',
                'is_monitor': False
            }
        ]

        created_count = 0
        for user_data in test_users:
            # Проверяем существует ли пользователь
            user_exists = User.objects.filter(username=user_data['username']).exists()
            
            if not user_exists:
                # Создаем пользователя Django
                user = User.objects.create(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_staff=user_data['username'] == 'admin',
                    is_superuser=user_data['username'] == 'admin'
                )
                user.set_password(user_data['password'])
                user.save()
                
                # Профиль создастся автоматически через сигнал
                # Обновляем профиль
                try:
                    profile = StudentProfile.objects.get(user=user)
                    profile.student_id = user_data['student_id']
                    profile.faculty = user_data['faculty']
                    profile.course = user_data['course']
                    profile.group = user_data['group']
                    profile.is_monitor = user_data['is_monitor']
                    profile.save()
                except StudentProfile.DoesNotExist:
                    StudentProfile.objects.create(
                        user=user,
                        student_id=user_data['student_id'],
                        faculty=user_data['faculty'],
                        course=user_data['course'],
                        group=user_data['group'],
                        is_monitor=user_data['is_monitor']
                    )
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создан пользователь: {user_data["username"]}')
                )
            else:
                # Обновляем существующего пользователя
                user = User.objects.get(username=user_data['username'])
                user.email = user_data['email']
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.is_staff = user_data['username'] == 'admin'
                user.is_superuser = user_data['username'] == 'admin'
                user.set_password(user_data['password'])
                user.save()
                
                # Обновляем профиль
                try:
                    profile = StudentProfile.objects.get(user=user)
                    profile.student_id = user_data['student_id']
                    profile.faculty = user_data['faculty']
                    profile.course = user_data['course']
                    profile.group = user_data['group']
                    profile.is_monitor = user_data['is_monitor']
                    profile.save()
                except StudentProfile.DoesNotExist:
                    StudentProfile.objects.create(
                        user=user,
                        student_id=user_data['student_id'],
                        faculty=user_data['faculty'],
                        course=user_data['course'],
                        group=user_data['group'],
                        is_monitor=user_data['is_monitor']
                    )
                
                self.stdout.write(
                    self.style.WARNING(f'Обновлен пользователь: {user_data["username"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Обработано {len(test_users)} тестовых пользователей')
        )