from django.contrib.auth.models import User

class CustomLDAPBackend:
    """
    Кастомный LDAP бэкенд для проверки доступа через группы
    Использует тестовые данные для разработки
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Тестовая аутентификация для разработки"""
        # Импортируем тестовые данные
        try:
            from identica.ldap_test_server import LDAP_TEST_USERS
        except ImportError:
            # Если файла нет, создаем базовых пользователей
            return self._create_fallback_user(username, password)
        
        # Проверяем существование пользователя
        if username not in LDAP_TEST_USERS:
            return None
        
        user_data = LDAP_TEST_USERS[username]
        
        # Проверяем пароль
        if user_data['password'] != password:
            return None
        
        # Проверяем доступ к приложению
        if 'identica-users' not in user_data['groups']:
            return None
        
        # Создаем или получаем пользователя Django
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'], 
                'last_name': user_data['last_name'],
                'is_staff': 'staff' in user_data['groups'],
                'is_superuser': 'admins' in user_data['groups'],
                'is_active': True
            }
        )
        
        if not created:
            # Обновляем данные существующего пользователя
            user.email = user_data['email']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name'] 
            user.is_staff = 'staff' in user_data['groups']
            user.is_superuser = 'admins' in user_data['groups']
            user.is_active = True
            user.save()
        
        return user
    
    def _create_fallback_user(self, username, password):
        """Создает тестового пользователя если файл с данными отсутствует"""
        # Базовые тестовые пользователи
        test_users = {
            'student1': {'password': 'password123', 'is_staff': False, 'is_superuser': False},
            'admin': {'password': 'admin123', 'is_staff': True, 'is_superuser': True},
        }
        
        if username not in test_users:
            return None
            
        if test_users[username]['password'] != password:
            return None
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@university.local',
                'first_name': username.capitalize(),
                'last_name': 'Тестовый',
                'is_staff': test_users[username]['is_staff'],
                'is_superuser': test_users[username]['is_superuser'],
                'is_active': True
            }
        )
        
        return user
    
    def get_user(self, user_id):
        """Получает пользователя по ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None