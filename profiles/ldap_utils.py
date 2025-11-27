from django.conf import settings

def check_website_access(username, website_url):
    """
    Проверяет, есть ли у пользователя доступ к указанному сайту
    На основе тестовых групп
    """
    # Получаем группы пользователя
    user_groups = get_user_groups(username)
    
    # Простые правила доступа для тестирования
    access_rules = {
        'https://library.university.local': ['students', 'staff', 'admins'],
        'https://research.university.local': ['staff', 'admins', 'monitors'], 
        'https://admin.university.local': ['staff', 'admins'],
        'https://courses.university.local': ['students', 'staff', 'admins', 'monitors'],
        'http://library.university.local': ['students', 'staff', 'admins'],
        'http://research.university.local': ['staff', 'admins', 'monitors'],
        'http://admin.university.local': ['staff', 'admins'],
        'http://courses.university.local': ['students', 'staff', 'admins', 'monitors'],
        'library.university.local': ['students', 'staff', 'admins'],
        'research.university.local': ['staff', 'admins', 'monitors'],
        'admin.university.local': ['staff', 'admins'],
        'courses.university.local': ['students', 'staff', 'admins', 'monitors'],
        'yandex.ru': ['students', 'staff', 'admins', 'monitors'],  # Все имеют доступ
        'google.com': ['students', 'staff', 'admins', 'monitors'], # Все имеют доступ
        'github.com': ['staff', 'admins'],  # Только персонал
    }
    
    # Нормализуем URL (убираем протокол для сравнения)
    normalized_url = website_url.replace('https://', '').replace('http://', '').replace('www.', '')
    
    # Проверяем доступ к сайту
    required_groups = access_rules.get(website_url, []) or access_rules.get(normalized_url, [])
    if not required_groups:  # Если сайта нет в правилах - доступ запрещен
        return False
    
    # Проверяем, есть ли у пользователя хотя бы одна из требуемых групп
    return any(group in user_groups for group in required_groups)

def get_user_groups(username):
    """Получает группы пользователя"""
    try:
        from identica.ldap_test_server import LDAP_TEST_USERS
        return LDAP_TEST_USERS.get(username, {}).get('groups', [])
    except ImportError:
        # Возвращаем группы по умолчанию для тестирования
        default_groups = {
            'student1': ['students', 'identica-users'],
            'student2': ['students', 'identica-users'],
            'monitor1': ['students', 'identica-users', 'monitors'],
            'admin': ['staff', 'identica-users', 'admins'],
        }
        return default_groups.get(username, ['identica-users'])

def get_user_accessible_websites(username):
    """Возвращает список сайтов, к которым у пользователя есть доступ"""
    user_groups = get_user_groups(username)
    
    # Все доступные сайты для тестирования
    all_websites = {
        'Библиотека университета': {
            'url': 'https://library.university.local',
            'required_groups': ['students', 'staff', 'admins'],
            'description': 'Доступ к электронной библиотеке'
        },
        'Научный портал': {
            'url': 'https://research.university.local', 
            'required_groups': ['staff', 'admins', 'monitors'],
            'description': 'Научные публикации и исследования'
        },
        'Админ панель': {
            'url': 'https://admin.university.local',
            'required_groups': ['staff', 'admins'],
            'description': 'Администрирование системы'
        },
        'Курсы и обучение': {
            'url': 'https://courses.university.local',
            'required_groups': ['students', 'staff', 'admins', 'monitors'],
            'description': 'Онлайн курсы и материалы'
        },
        'Яндекс': {
            'url': 'https://yandex.ru',
            'required_groups': ['students', 'staff', 'admins', 'monitors'],
            'description': 'Поисковая система'
        },
        'Google': {
            'url': 'https://google.com',
            'required_groups': ['students', 'staff', 'admins', 'monitors'],
            'description': 'Поисковая система'
        },
        'GitHub': {
            'url': 'https://github.com',
            'required_groups': ['staff', 'admins'],
            'description': 'Платформа для разработчиков'
        },
    }
    
    accessible_websites = []
    for name, site_info in all_websites.items():
        if any(group in user_groups for group in site_info['required_groups']):
            accessible_websites.append({
                'name': name,
                'url': site_info['url'],
                'description': site_info['description'],
                'access_granted': True
            })
        else:
            accessible_websites.append({
                'name': name,
                'url': site_info['url'], 
                'description': site_info['description'],
                'access_granted': False
            })
    
    return accessible_websites

def get_user_ldap_info(username):
    """Возвращает информацию о пользователе из LDAP"""
    try:
        from identica.ldap_test_server import LDAP_TEST_USERS
        user_data = LDAP_TEST_USERS.get(username, {})
        return {
            'username': username,
            'groups': user_data.get('groups', []),
            'email': user_data.get('email', ''),
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
        }
    except ImportError:
        return {
            'username': username,
            'groups': ['identica-users'],
            'email': f'{username}@university.local',
            'first_name': 'Тестовый',
            'last_name': 'Пользователь',
        }

def check_website_access(username, website_url):
    """
    Проверяет, есть ли у пользователя доступ к указанному сайту
    На основе тестовых групп
    """
    # Получаем группы пользователя
    user_groups = get_user_groups(username)
    
    # Правила доступа к НАШИМ тестовым страницам
    access_rules = {
        # Наши внутренние тестовые страницы
        'https://library.identica.local': ['students', 'staff', 'admins'],
        'https://research.identica.local': ['staff', 'admins', 'monitors'], 
        'https://admin.identica.local': ['staff', 'admins'],
        'https://courses.identica.local': ['students', 'staff', 'admins', 'monitors'],
        'http://library.identica.local': ['students', 'staff', 'admins'],
        'http://research.identica.local': ['staff', 'admins', 'monitors'],
        'http://admin.identica.local': ['staff', 'admins'],
        'http://courses.identica.local': ['students', 'staff', 'admins', 'monitors'],
        'library.identica.local': ['students', 'staff', 'admins'],
        'research.identica.local': ['staff', 'admins', 'monitors'],
        'admin.identica.local': ['staff', 'admins'],
        'courses.identica.local': ['students', 'staff', 'admins', 'monitors'],
    }
    
    # Нормализуем URL
    normalized_url = website_url.replace('https://', '').replace('http://', '').replace('www.', '')
    
    # Проверяем доступ к сайту
    required_groups = access_rules.get(website_url, []) or access_rules.get(normalized_url, [])
    if not required_groups:  # Если сайта нет в правилах - доступ запрещен
        return False
    
    # Проверяем, есть ли у пользователя хотя бы одна из требуемых групп
    return any(group in user_groups for group in required_groups)

def get_user_accessible_websites(username):
    """Возвращает список сайтов, к которым у пользователя есть доступ"""
    user_groups = get_user_groups(username)
    
    # Наши тестовые сайты
    all_websites = {
        'Библиотека университета': {
            'url': '/test/library/',
            'external_url': 'https://library.identica.local',
            'required_groups': ['students', 'staff', 'admins'],
            'description': 'Доступ к электронной библиотеке'
        },
        'Научный портал': {
            'url': '/test/research/',
            'external_url': 'https://research.identica.local', 
            'required_groups': ['staff', 'admins', 'monitors'],
            'description': 'Научные публикации и исследования'
        },
        'Админ панель': {
            'url': '/test/admin/',
            'external_url': 'https://admin.identica.local',
            'required_groups': ['staff', 'admins'],
            'description': 'Администрирование системы'
        },
        'Курсы и обучение': {
            'url': '/test/courses/',
            'external_url': 'https://courses.identica.local',
            'required_groups': ['students', 'staff', 'admins', 'monitors'],
            'description': 'Онлайн курсы и материалы'
        },
    }
    
    accessible_websites = []
    for name, site_info in all_websites.items():
        if any(group in user_groups for group in site_info['required_groups']):
            accessible_websites.append({
                'name': name,
                'url': site_info['url'],  # Внутренний URL
                'external_url': site_info['external_url'],  # Для проверки LDAP
                'description': site_info['description'],
                'access_granted': True
            })
        else:
            accessible_websites.append({
                'name': name,
                'url': site_info['url'],
                'external_url': site_info['external_url'],
                'description': site_info['description'],
                'access_granted': False
            })
    
    return accessible_websites