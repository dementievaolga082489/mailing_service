from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Client(models.Model):
    """Получатель рассылки"""

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, verbose_name="Ф.И.О.")
    comment = models.TextField(max_length=255, verbose_name="Комментарии", blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="clients", verbose_name="Владелец"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Message(models.Model):
    """Сообщение для рассылки"""

    subject = models.CharField(max_length=255, verbose_name="Тема сообщения")
    body = models.TextField(max_length=1000, verbose_name="Текст сообщения")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages", verbose_name="Владелец"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    """Рассылка"""

    STATUS_CHOICES = [
        ("created", "Создана"),
        ("running", "Запущена"),
        ("completed", "Завершена"),
        ("disabled", "Отключена"),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        Client, related_name="mailings", verbose_name="Получатели"
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="mailings", verbose_name="Владелец"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def update_status(self):
        """Обновление статуса на основе текущего времени"""
        if not self.is_active:
            self.status = "disabled"
            self.save(update_fields=["status"])
            return

        now = timezone.now()
        if now < self.start_time:
            new_status = "created"
        elif self.start_time <= now <= self.end_time:
            new_status = "running"
        else:
            new_status = "completed"

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])

    def get_recipients_count(self):
        """Получение количества получателей"""
        return self.recipients.count()

    def __str__(self):
        return f"Рассылка #{self.id}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class MailingAttempt(models.Model):
    """Попытка отправки"""

    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус"
    )
    server_response = models.TextField(blank=True, verbose_name="Ответ сервера")
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="attempts", verbose_name="Клиент"
    )

    def __str__(self):
        return f"Попытка #{self.id} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"
        ordering = ["-attempt_time"]
