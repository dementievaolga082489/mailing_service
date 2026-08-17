from django import forms
from django.core.exceptions import ValidationError
from django.forms import BooleanField
from django.utils import timezone

from mailing.models import Client, Message, Mailing


class StyleFormMixin:

    def __init__(self, *args, **kwargs):
        """Инициализация формы с добавлением CSS-классов Bootstrap"""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Проверяем, что поле имеет widget и attrs
            if hasattr(field, "widget") and hasattr(field.widget, "attrs"):
                if isinstance(field, BooleanField):
                    field.widget.attrs["class"] = "form-check-input"
                else:
                    field.widget.attrs["class"] = "form-control"


class ClientForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Client.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Клиент с таким email уже существует")
        return email


class MessageForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 5}),
        }


class MailingForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_time", "end_time", "message", "recipients"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "recipients": forms.SelectMultiple(
                attrs={"size": 8, "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)

        if owner:
            # Фильтруем сообщения и клиентов по владельцу
            self.fields["message"].queryset = Message.objects.filter(owner=owner)
            self.fields["recipients"].queryset = Client.objects.filter(owner=owner)

            # Добавляем отладочную информацию (можно убрать в продакшене)
            print(f"=== Отладка MailingForm ===")
            print(f"Пользователь: {owner}")
            print(f"Доступно сообщений: {self.fields['message'].queryset.count()}")
            print(f"Доступно клиентов: {self.fields['recipients'].queryset.count()}")

            # Если нет клиентов, добавляем подсказку
            if self.fields["recipients"].queryset.count() == 0:
                self.fields["recipients"].help_text = (
                    "⚠️ Нет доступных клиентов. Сначала создайте клиентов."
                )

            if self.fields["message"].queryset.count() == 0:
                self.fields["message"].help_text = (
                    "⚠️ Нет доступных сообщений. Сначала создайте сообщение."
                )
        else:
            print("⚠️ Внимание: owner не передан в форму!")

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        recipients = cleaned_data.get("recipients")

        # Проверка на наличие получателей
        if recipients and not recipients.exists():
            raise ValidationError("Необходимо выбрать хотя бы одного получателя")

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError("Дата начала должна быть раньше даты окончания")
            if start_time < timezone.now():
                raise ValidationError("Дата начала не может быть в прошлом")

        return cleaned_data
