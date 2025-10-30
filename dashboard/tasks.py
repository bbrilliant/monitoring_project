import logging
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from .models import MonitoredAPI
from .utils import check_api_health 

logger = logging.getLogger(__name__)

@shared_task
def send_daily_api_report():
    apis = MonitoredAPI.objects.all()
    up_apis = []
    down_apis = []

    for api in apis:
        is_up = check_api_health(api.url)
        (up_apis if is_up else down_apis).append(api)
        print(is_up)

    context = {
        'apis_down': down_apis,
        'company_name': "ATOS MEDA TOGO",
        'logo_url': "https://upload.wikimedia.org/wikipedia/en/thumb/0/01/Atos.svg/474px-Atos.svg.png?20210828071521",
        'main_color': "#034D97",
    }

    html_content = render_to_string('emails/daily_report.html', context)
    subject = f"Rapport journalier des APIs - {context['company_name']}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = ["bright.amegnaglo@atos.net", "bamegnaglo@gmail.com"]

    msg = EmailMultiAlternatives(subject, "", from_email, to)
    msg2 = EmailMultiAlternatives("Test", "This is a test email", from_email, ["bamegnaglo@gmail.com", "bright.amegnaglo@atos.net"])
    msg.attach_alternative(html_content, "text/html")
    try:
        print("🔹 Tentative d’envoi d’e-mail...")
        msg.send()
        msg2.send()
        print("✅ E-mail envoyé avec succès.")
    except Exception as e:
        print(f"❌ Erreur d’envoi d’e-mail : {e}")
        logger.exception("Erreur lors de l’envoi du mail quotidien")
