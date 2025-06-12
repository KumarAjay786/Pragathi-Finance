import string
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from .models import AdvisoryApplication, FinancialServices


def generate_random_password(length=8):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))


def handle_user_creation_and_email(full_name, email, extra_message=""):
    UserModel = get_user_model()

    if not UserModel.objects.filter(email=email).exists():
        password = generate_random_password()
        user = UserModel.objects.create_user(
            email=email,
            password=password,
            name=full_name  # Ensure your User model has a `name` field
        )
        user.save()

        # Email to user (new account)
        user_msg = (
            f"Dear {full_name},\n\n"
            f"{extra_message}\n\n"
            f"Here are your login credentials:\n"
            f"Email: {email}\n"
            f"Password: {password}\n\n"
            f"Login at: http://pragathifs.com/login/\n\n"
            f"Regards,\nPragathi Finance Solutions"
        )
        send_mail(
            subject="Form Submitted - Login Credentials",
            message=user_msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    else:
        # User already exists
        user_msg = (
            f"Dear {full_name},\n\n"
            f"{extra_message}\n\n"
            f"You already have an account with us. Please use your existing credentials.\n"
            f"If you forgot your password, use the reset option on the login page.\n\n"
            f"Regards,\nPragathi Finance Solutions"
        )
        send_mail(
            subject="Form Submitted - Account Exists",
            message=user_msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )


@receiver(post_save, sender=AdvisoryApplication)
def handle_advisory_application(sender, instance, created, **kwargs):
    if created:
        email = instance.email
        full_name = instance.name

        # Admin Email
        admin_html = f"""
<p><strong>New Investment Inquiry Received</strong></p>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
    <tr><td><strong>Name</strong></td><td>{instance.name}</td></tr>
    <tr><td><strong>Gender</strong></td><td>{instance.gender}</td></tr>
    <tr><td><strong>Year of Birth</strong></td><td>{instance.dob}</td></tr>
    <tr><td><strong>Email ID</strong></td><td>{instance.email}</td></tr>
    <tr><td><strong>Mobile No</strong></td><td>{instance.mobile}</td></tr>
    <tr><td><strong>Address</strong></td><td>{instance.address}</td></tr>
    <tr><td><strong>Interest of Invest In</strong></td><td>{instance.interest_invest}</td></tr>
    <tr><td><strong>Interest In</strong></td><td>{instance.interest}</td></tr>
    <tr><td><strong>Range of Investment</strong></td><td>{instance.range_investment}</td></tr>
    <tr><td><strong>Expected ROI</strong></td><td>{instance.expected_roi}</td></tr>
    <tr><td><strong>Duration of Investment</strong></td><td>{instance.duration}</td></tr>
</table>
"""
        send_mail(
            subject="New Advisory Application Received",
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=admin_html,
            fail_silently=False,
        )

        extra_msg = (
            "Thank you for submitting your advisory form.\n"
            "We will review your application and get back to you soon."
        )
        handle_user_creation_and_email(full_name, email, extra_msg)


@receiver(post_save, sender=FinancialServices)
def handle_financial_application(sender, instance, created, **kwargs):
    if created:
        email = instance.email
        full_name = instance.company_name

        # Admin Email
        admin_html = f"""
            <p><strong>New Financial Inquiry Received</strong></p>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
                <tr><td><strong>Company Name</strong></td><td>{instance.company_name}</td></tr>
                <tr><td><strong>Legal Status</strong></td><td>{instance.legal_status}</td></tr>
                <tr><td><strong>Contact Person</strong></td><td>{instance.contact_person}</td></tr>
                <tr><td><strong>Email</strong></td><td>{instance.email}</td></tr>
                <tr><td><strong>Mobile</strong></td><td>{instance.mobile}</td></tr>
                <tr><td><strong>City</strong></td><td>{instance.city}</td></tr>
                <tr><td><strong>Country</strong></td><td>{instance.country}</td></tr>
                <tr><td><strong>Nature of Business</strong></td><td>{instance.nature_of_business}</td></tr>
                <tr><td><strong>Net Worth</strong></td><td>{instance.net_worth}</td></tr>
                <tr><td><strong>Last Turnover</strong></td><td>{instance.last_turnover}</td></tr>
                <tr><td><strong>Loan Liability</strong></td><td>{instance.current_loan_liability}</td></tr>
                <tr><td><strong>IT Paid</strong></td><td>{instance.last_it_paid}</td></tr>
                <tr><td><strong>Fund Required</strong></td><td>{instance.fund_looking_for}</td></tr>
                <tr><td><strong>Funding Purpose</strong></td><td>{instance.purpose_of_funding}</td></tr>
                <tr><td><strong>Nature of Funding</strong></td><td>{instance.nature_of_funding}</td></tr>
                <tr><td><strong>Offered ROI</strong></td><td>{instance.offered_roi}</td></tr>
            </table>
        """
        send_mail(
            subject="New Financial Inquiry Received",
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=admin_html,
            fail_silently=False,
        )

        extra_msg = (
            "Thank you for submitting your financial inquiry form.\n"
            "We will review your submission and contact you shortly."
        )
        handle_user_creation_and_email(full_name, email, extra_msg)
