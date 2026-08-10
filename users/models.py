from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""

    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )
    is_email_verified = models.BooleanField(
        default=False, verbose_name="Email подтвержден"
    )
    email_verification_token = models.CharField(
        max_length=100, blank=True, verbose_name="Токен верификации"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_view_all_mailings", "Может просматривать все рассылки"),
            ("can_view_all_clients", "Может просматривать всех клиентов"),
            ("can_block_users", "Может блокировать пользователей"),
            ("can_disable_mailings", "Может отключать рассылки"),
        ]

    def __str__(self):
        return self.email

    @property
    def is_manager(self):
        return self.has_perm("users.can_view_all_mailings")
