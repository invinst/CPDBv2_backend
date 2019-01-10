from anymail.backends.mailgun import EmailBackend
from bandit.backends.base import HijackBackendMixin


# pragma: no cover
class MailGunHijackBackend(HijackBackendMixin, EmailBackend):
    """
    This backend intercepts outgoing messages drops them to a single email
    address, using the Anymail EmailBackend.
    """
    pass
