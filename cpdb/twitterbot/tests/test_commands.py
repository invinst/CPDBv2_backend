from django.test import SimpleTestCase
from django.core.management import call_command

from mock import patch


class CommandTestCase(SimpleTestCase):
    def test_start_twitterbot(self):
        with patch('responsebot.responsebot.ResponseBot.start') as start_method:
            call_command('start_twitterbot')
            start_method.assert_called()
