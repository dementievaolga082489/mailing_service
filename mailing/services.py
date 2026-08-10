from django.core.mail import send_mail
from django.conf import settings
from .models import MailingAttempt


def send_mailing(mailing):
    """Отправка рассылки"""
    result = {"success": False, "success_count": 0, "failed_count": 0, "error": None}

    try:
        recipients = mailing.recipients.all()
        message = mailing.message

        for client in recipients:
            try:
                # Отправка письма
                send_mail(
                    subject=message.subject,
                    message=message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )

                # Создание записи об успешной попытке
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status="success",
                    server_response="Письмо успешно отправлено",
                    client=client,
                )
                result["success_count"] += 1

            except Exception as e:
                # Создание записи о неудачной попытке
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status="failed",
                    server_response=str(e),
                    client=client,
                )
                result["failed_count"] += 1

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)

    return result
