from django.contrib import admin
from .models import Client, Message, Mailing, MailingAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "email", "owner", "created_at"]
    list_filter = ["owner", "created_at"]
    search_fields = ["full_name", "email"]
    # Убираем full_name из list_editable, если он в list_display_links
    # Или убираем из list_display_links
    list_display_links = ["id", "full_name"]  # Оставляем здесь
    list_editable = ["email"]  # Убираем full_name отсюда
    readonly_fields = ["created_at"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "subject", "owner", "created_at"]
    list_filter = ["owner", "created_at"]
    search_fields = ["subject", "body"]
    list_display_links = ["id", "subject"]
    list_editable = (
        []
    )  # Пустой список или только поля, которых нет в list_display_links
    readonly_fields = ["created_at"]


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "start_time",
        "end_time",
        "status",
        "is_active",
        "owner",
        "created_at",
    ]
    list_filter = ["status", "is_active", "owner", "created_at"]
    search_fields = ["message__subject"]
    list_display_links = ["id"]
    list_editable = ["status", "is_active"]
    readonly_fields = ["created_at"]
    filter_horizontal = ["recipients"]


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "mailing", "client", "status", "attempt_time"]
    list_filter = ["status", "attempt_time", "mailing"]
    search_fields = ["mailing__message__subject", "client__email"]
    list_display_links = ["id"]
    list_editable = []  # Попытки не должны быть редактируемыми
    readonly_fields = ["attempt_time", "mailing", "client", "status", "server_response"]
