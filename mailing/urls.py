from mailing.apps import MailingConfig

from django.urls import path
from .views import (
    ClientListView,
    ClientCreateView,
    ClientUpdateView,
    ClientDeleteView,
    MessageListView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    MailingListView,
    MailingDetailView,
    MailingCreateView,
    MailingUpdateView,
    MailingDeleteView,
    send_mailing_view,
    statistics_view,
    toggle_mailing_status,
)

app_name = MailingConfig.name

urlpatterns = [
    # Клиенты
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/create/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/edit/", ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    # Сообщения
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/edit/", MessageUpdateView.as_view(), name="message_update"),
    path("messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    # Рассылки
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:pk>/edit/", MailingUpdateView.as_view(), name="mailing_update"),
    path(
        "mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path("mailings/<int:pk>/send/", send_mailing_view, name="mailing_send"),
    path("mailings/<int:pk>/toggle/", toggle_mailing_status, name="mailing_toggle"),
    # Статистика
    path("statistics/", statistics_view, name="statistics"),
]
