from django.core.management.base import BaseCommand
from profiles.models import Website, WebsiteCategory

class Command(BaseCommand):
    help = 'Создает тестовые сайты для системы подписок'

    def handle(self, *args, **options):
        # Создаем категории
        categories = {
            'education': 'Образовательные платформы',
            'programming': 'Программирование и IT',
            'design': 'Дизайн и креатив',
            'science': 'Научные ресурсы',
        }
        
        created_categories = {}
        for slug, name in categories.items():
            category, created = WebsiteCategory.objects.get_or_create(
                name=name,
                defaults={'description': f'Ресурсы в категории {name}'}
            )
            created_categories[slug] = category
            if created:
                self.stdout.write(f'Создана категория: {name}')

        # Создаем тестовые сайты
        test_websites = [
            {
                'name': 'Coursera - Онлайн курсы',
                'url': 'https://www.coursera.org',
                'category': created_categories['education'],
                'description': 'Платформа онлайн-курсов от ведущих университетов мира',
                'subscription_type': 'auto',
                'requires_approval': False,
                'duration_days': 90,
            },
            {
                'name': 'edX - Образовательная платформа',
                'url': 'https://www.edx.org',
                'category': created_categories['education'],
                'description': 'Онлайн-курсы от Гарварда, MIT и других университетов',
                'subscription_type': 'auto', 
                'requires_approval': False,
                'duration_days': 180,
            },
            {
                'name': 'GitHub Student Pack',
                'url': 'https://education.github.com/pack',
                'category': created_categories['programming'],
                'description': 'Бесплатные инструменты для студентов от GitHub',
                'subscription_type': 'manual',
                'requires_approval': True,
                'duration_days': 365,
            },
            {
                'name': 'JetBrains IDE',
                'url': 'https://www.jetbrains.com/student/',
                'category': created_categories['programming'],
                'description': 'Бесплатные лицензии на IDE для студентов',
                'subscription_type': 'manual',
                'requires_approval': True,
                'duration_days': 365,
            },
            {
                'name': 'Figma Education',
                'url': 'https://www.figma.com/education/',
                'category': created_categories['design'],
                'description': 'Профессиональный инструмент для дизайна',
                'subscription_type': 'manual',
                'requires_approval': True,
                'duration_days': 365,
            },
            {
                'name': 'Adobe Creative Cloud',
                'url': 'https://www.adobe.com/creativecloud/buy/students.html',
                'category': created_categories['design'],
                'description': 'Пакет творческих приложений со скидкой для студентов',
                'subscription_type': 'manual',
                'requires_approval': True,
                'duration_days': 365,
            },
            {
                'name': 'Google Scholar',
                'url': 'https://scholar.google.com',
                'category': created_categories['science'],
                'description': 'Поиск научной литературы',
                'subscription_type': 'auto',
                'requires_approval': False,
                'duration_days': 0,  # Бессрочная
            },
            {
                'name': 'ResearchGate',
                'url': 'https://www.researchgate.net',
                'category': created_categories['science'],
                'description': 'Социальная сеть для ученых и исследователей',
                'subscription_type': 'auto',
                'requires_approval': False,
                'duration_days': 0,  # Бессрочная
                
            },
            {
                'name': 'Преподавательский портал',
                'url': 'https://university-teacher-portal.example.com',
                'category': created_categories['education'],
                'description': 'Внутренний портал для преподавателей университета',
                'subscription_type': 'auto',
                'requires_approval': False,
                'duration_days': 365,
                'access_level': 'teachers',
            },
            {
                'name': 'Кураторская аналитика',
                'url': 'https://curator-analytics.example.com',
                'category': created_categories['education'],
                'description': 'Аналитика успеваемости и активности студентов',
                'subscription_type': 'auto',
                'requires_approval': False,
                'duration_days': 365,
                'access_level': 'curators',
            },
            {
                'name': 'Портал старост',
                'url': 'https://monitor-portal.example.com',
                'category': created_categories['education'],
                'description': 'Сервис для управления группой и коммуникации',
                'subscription_type': 'auto',
                'requires_approval': False,
                'duration_days': 365,
                'access_level': 'monitors',
            },
        ]

        created_count = 0
        for site_data in test_websites:
            website, created = Website.objects.get_or_create(
                name=site_data['name'],
                defaults=site_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Создан сайт: {site_data["name"]}')

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {created_count} тестовых сайтов!')
        )