"""
Тестовый LDAP сервер для разработки на Windows
"""
import os
from django.conf import settings

# Тестовые данные LDAP для разработки
LDAP_TEST_USERS = {
    'student1': {
        'password': 'password123',
        'groups': ['students', 'identica-users'],
        'email': 'student1@university.local',
        'first_name': 'Иван',
        'last_name': 'Петров'
    },
    'student2': {
        'password': 'password123', 
        'groups': ['students', 'identica-users'],
        'email': 'student2@university.local',
        'first_name': 'Мария',
        'last_name': 'Сидорова'
    },
    'monitor1': {
        'password': 'password123',
        'groups': ['students', 'identica-users', 'monitors'],
        'email': 'monitor1@university.local', 
        'first_name': 'Алексей',
        'last_name': 'Иванов'
    },
    'admin': {
        'password': 'admin123',
        'groups': ['staff', 'identica-users', 'admins'],
        'email': 'admin@university.local',
        'first_name': 'Администратор',
        'last_name': 'Системы'
    }
}

LDAP_TEST_GROUPS = {
    'identica-users': ['student1', 'student2', 'monitor1', 'admin'],
    'students': ['student1', 'student2', 'monitor1'],
    'monitors': ['monitor1'],
    'staff': ['admin'],
    'admins': ['admin']
}