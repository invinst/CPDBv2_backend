from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.requests import RequestSite


def send_forgot_password_email(request, user):
    request_site = RequestSite(request)
    site_name = request_site.name
    domain = request_site.domain
    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
        'user': user,
        'token': default_token_generator.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    }

    subject = loader.render_to_string('registration/password_reset_subject.txt', context)
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string('registration/password_reset_email.html', context)
    email_message = EmailMultiAlternatives(subject, body, None, [user.email])

    email_message.send()
