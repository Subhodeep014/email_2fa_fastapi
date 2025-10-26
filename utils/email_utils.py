# app/utils/email_utils.py
import os
from sib_api_v3_sdk import Configuration, ApiClient, TransactionalEmailsApi, SendSmtpEmail
from dotenv import load_dotenv

load_dotenv()
def send_verification_code_email(to_email: str, code: str):
    configuration = Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
    api_instance = TransactionalEmailsApi(ApiClient(configuration))

    email = SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"name": os.getenv("SENDER_NAME"), "email": os.getenv("SENDER_EMAIL")},
        subject="Your Verification Code",
        html_content=f"<html><body><h2>Your verification code is: <b>{code}</b></h2><p>This code expires in 10 minutes.</p></body></html>"
    )

    api_instance.send_transac_email(email)
