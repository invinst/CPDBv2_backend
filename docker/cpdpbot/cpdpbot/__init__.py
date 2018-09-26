import logging.config
import os
import socket
import ssl

syslog_host = os.environ.get('PAPERTRAIL_ENDPOINT', '')
syslog_port = int(os.environ.get('PAPERTRAIL_PORT', 0))
syslog_cert_path = '/etc/papertrail-bundle.pem'


class _ContextFilter(logging.Filter):
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = _ContextFilter.hostname
        return True


if os.environ.get('SETUP_LOGGING', 'yes') != 'no':
    logging.config.dictConfig({
        'version': 1,
        'filters': {
            'context': {
                '()': _ContextFilter
            }
        },
        'formatters': {
            'simple': {
                'format': '%(asctime)s %(hostname)s Twitterbot: %(levelname)s %(message)s',
                'datefmt': '%Y-%m-%dT%H:%M:%S',
            },
        },
        'handlers': {
            'syslog': {
                'level': 'INFO',
                'class': 'tlssyslog.TLSSysLogHandler',
                'formatter': 'simple',
                'filters': ['context'],
                'address': (syslog_host, syslog_port),
                'ssl_kwargs': {
                    'cert_reqs': ssl.CERT_REQUIRED,
                    'ssl_version': ssl.PROTOCOL_TLS,
                    'ca_certs': syslog_cert_path,
                },
            },
        },
        'loggers': {
            'main': {
                'handlers': ['syslog'],
                'level': 'INFO',
            }
        }
    })
