import logging

import sib_api_v3_sdk
from celery import shared_task
from sib_api_v3_sdk.rest import ApiException

from extensions import brevo_api


@shared_task
def send_activation_email(email, template):
    email_obj = sib_api_v3_sdk.SendSmtpEmail(
        sender=sib_api_v3_sdk.SendSmtpEmailSender(
            name="John Smith", email="app@example.com"
        ),
        to=[sib_api_v3_sdk.SendSmtpEmailTo(email=email, name="App user")],
        subject="Account activation",
        html_content=template,
    )
    try:
        api_response = brevo_api.send_transac_email(email_obj)
        logging.info(f"Sending activation email to {email}")
    except ApiException as e:
        logging.warning(
            f"Error occured when attempting to send activation email to {email} : {e}"
        )
        return False
    return True
