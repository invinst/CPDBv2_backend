from django.test import SimpleTestCase
from django.core.management import call_command

from mock import patch
from robber import expect


class RebuildIndexDailyCommandTestCase(SimpleTestCase):
    def test_handle(self):
        with patch('es_index.management.commands.rebuild_index_daily.call_command') as call_command_mock:
            call_command('rebuild_index_daily')
            called_args = call_command_mock.call_args_list
            expect(call_command_mock.call_count).to.eq(2)
            rebuild_index_args = called_args[0][0]
            rebuild_search_index_args = called_args[1][0]

            expect(rebuild_index_args[0]).to.eq('rebuild_index')
            expect(rebuild_index_args[1]).to.eq('--daily')
            expect(rebuild_search_index_args[0]).to.eq('rebuild_search_index')
            expect(rebuild_search_index_args[1]).to.eq('--daily')
