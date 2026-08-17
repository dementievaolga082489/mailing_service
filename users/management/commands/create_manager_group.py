from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Создает группу менеджеров с соответствующими правами"

    def handle(self, *args, **options):
        # Создаем группу
        group, created = Group.objects.get_or_create(name="Менеджеры")

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана'))
        else:
            self.stdout.write('Группа "Менеджеры" уже существует')

        # Список необходимых прав
        permissions_codenames = [
            "can_view_all_mailings",
            "can_view_all_clients",
            "can_block_users",
            "can_disable_mailings",
        ]

        # Добавляем права в группу
        for codename in permissions_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
                self.stdout.write(f"Добавлено право: {codename}")
            except Permission.DoesNotExist:
                self.stdout.write(f"Право не найдено: {codename}")

        self.stdout.write(self.style.SUCCESS("\nГруппа менеджеров настроена!"))
