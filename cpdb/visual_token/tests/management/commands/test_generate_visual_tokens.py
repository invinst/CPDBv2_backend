from django.test import SimpleTestCase, override_settings
from django.core.management import call_command

from mock import patch, Mock

from officers.doc_types import OfficerInfoDocType
from officers.index_aliases import officers_index_alias


class CommandTestCase(SimpleTestCase):
    figure = Mock()

    def setUp(self):
        for doc in OfficerInfoDocType().search().scan():
            doc.delete()

    @patch('visual_token.management.commands.generate_visual_tokens.ChartFigure', return_value=figure)
    @patch('visual_token.management.commands.generate_visual_tokens.clear_folder')
    @override_settings(VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER='/media')
    def test_invocation(self, clear_folder, ChartFigure):
        OfficerInfoDocType(
            id='1234',
            allegation_count=10,
            trr_count=12,
            percentiles=[
                {
                    'percentile_allegation_civilian': '62.175',
                    'percentile_allegation_internal': '60.545',
                    'percentile_trr': '58.606'
                }
            ]
        ).save(index=officers_index_alias.name)
        officers_index_alias.read_index.refresh()

        surface = Mock()
        self.figure.draw = Mock(return_value=surface)

        call_command('generate_visual_tokens')
        clear_folder.assert_called_with('/media')
        ChartFigure.assert_called_with(640, 640)
        self.figure.draw.assert_called_with([62.175, 60.545, 58.606])
        surface.write_to_png.assert_called_with('/media/officer_1234.png')

    @patch('visual_token.management.commands.generate_visual_tokens.ChartFigure', return_value=figure)
    @patch('visual_token.management.commands.generate_visual_tokens.clear_folder')
    @override_settings(VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER='/media')
    def test_ignore_officer_missing_data(self, clear_folder, ChartFigure):
        OfficerInfoDocType(
            id='1234',
            allegation_count=10,
            trr_count=12,
            percentiles=[
                {
                    'percentile_allegation_civilian': '62.175',
                    'percentile_allegation_internal': '60.545',
                    'percentile_trr': '58.606'
                }
            ]
        ).save(index=officers_index_alias.name)
        OfficerInfoDocType(
            id='1235',
            allegation_count=3,
            trr_count=2,
            percentiles=[
                {
                    'percentile_allegation_civilian': '43.175'
                }
            ]
        ).save(index=officers_index_alias.name)
        officers_index_alias.read_index.refresh()

        surface = Mock()
        self.figure.draw = Mock(return_value=surface)

        call_command('generate_visual_tokens')
        surface.write_to_png.assert_called_once_with('/media/officer_1234.png')
