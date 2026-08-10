from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
from .services import send_mailing


# region ГЛАВНАЯ СТРАНИЦА
def index(request):
    """Главная страница"""
    cache_key = "index_stats"
    stats = cache.get(cache_key)

    if stats is None:
        stats = {
            "total_mailings": Mailing.objects.count(),
            "active_mailings": Mailing.objects.filter(
                start_time__lte=timezone.now(),
                end_time__gte=timezone.now(),
                is_active=True,
            ).count(),
            "total_clients": Client.objects.count(),
        }
        cache.set(cache_key, stats, 300)

    return render(request, "mailing/index.html", {"stats": stats})


# endregion


# region УПРАВЛЕНИЕ КЛИЕНТАМИ (CRUD)
class ClientListView(LoginRequiredMixin, ListView):
    """Список клиентов"""

    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        if self.request.user.is_manager:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Создание клиента"""

    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование клиента"""

    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление клиента"""

    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


# endregion


# region УПРАВЛЕНИЕ СООБЩЕНИЯМИ (CRUD)
class MessageListView(LoginRequiredMixin, ListView):
    """Список сообщений"""

    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "message_list"

    def get_queryset(self):
        if self.request.user.is_manager:
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание сообщения"""

    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование сообщения"""

    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


class MessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление сообщения"""

    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


# endregion


# region УПРАВЛЕНИЕ РАССЫЛКАМИ (CRUD)
class MailingListView(LoginRequiredMixin, ListView):
    """Список рассылок"""

    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailing_list"

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_manager:
            queryset = Mailing.objects.all()
        else:
            queryset = Mailing.objects.filter(owner=self.request.user)

        queryset = queryset.select_related("message", "owner").prefetch_related(
            "recipients"
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for mailing in context["mailing_list"]:
            mailing.update_status()
        return context


class MailingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Детали рассылки"""

    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user or self.request.user.is_manager


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание рассылки"""

    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        self.object.update_status()
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование рассылки"""

    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def test_func(self):
        return self.get_object().owner == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.update_status()
        return response


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление рассылки"""

    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def test_func(self):
        return self.get_object().owner == self.request.user


# endregion


# region ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ
@login_required
def send_mailing_view(request, pk):
    """Ручной запуск рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk)

    if not (mailing.owner == request.user or request.user.is_manager):
        messages.error(request, "Нет прав")
        return redirect("mailing:mailing_detail", pk=pk)

    mailing.update_status()
    if mailing.status == "disabled":
        messages.error(request, "Рассылка отключена")
        return redirect("mailing:mailing_detail", pk=pk)

    result = send_mailing(mailing)

    if result["success"]:
        messages.success(
            request,
            f'Отправлено. Успешно: {result["success_count"]}, Ошибок: {result["failed_count"]}',
        )
    else:
        messages.error(request, result.get("error", "Ошибка отправки"))

    return redirect("mailing:mailing_detail", pk=pk)


@login_required
def statistics_view(request):
    """Статистика рассылок"""
    if request.user.is_manager:
        mailings = Mailing.objects.all()
    else:
        mailings = Mailing.objects.filter(owner=request.user)

    attempts = MailingAttempt.objects.filter(mailing__in=mailings)

    cache_key = f"stats_{request.user.id}"
    stats = cache.get(cache_key)

    if stats is None:
        stats = {
            "total_mailings": mailings.count(),
            "total_attempts": attempts.count(),
            "success_attempts": attempts.filter(status="success").count(),
            "failed_attempts": attempts.filter(status="failed").count(),
        }
        stats["success_rate"] = (
            (stats["success_attempts"] / stats["total_attempts"] * 100)
            if stats["total_attempts"] > 0
            else 0
        )
        cache.set(cache_key, stats, 300)

    return render(request, "mailing/statistics.html", {"stats": stats})


@login_required
def toggle_mailing_status(request, pk):
    """Вкл/Выкл рассылки (для менеджеров)"""
    if not request.user.is_manager:
        messages.error(request, "Нет прав")
        return redirect("mailing:mailing_detail", pk=pk)

    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.is_active = not mailing.is_active
    mailing.save()
    mailing.update_status()

    messages.success(
        request, f'Рассылка {"включена" if mailing.is_active else "отключена"}'
    )
    return redirect("mailing:mailing_detail", pk=pk)


# endregion
