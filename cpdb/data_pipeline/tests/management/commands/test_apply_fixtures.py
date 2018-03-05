from django.test import TestCase
from django.core.management import call_command, CommandError

from mock import patch, call, Mock
from robber import expect

from data_pipeline.models import AppliedFixture
from data_pipeline.factories import AppliedFixtureFactory


def mock_object(**kwargs):
    class MyObject(object):
        pass

    obj = MyObject()
    for key, val in kwargs.items():
        setattr(obj, key, val)
    return obj


mock_get_blob_to_path = Mock()


class ApplyFixturesCommandTestCase(TestCase):
    def setUp(self):
        mock_get_blob_to_path.reset()

    @patch('data_pipeline.management.commands.apply_fixtures.os.remove')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.NamedTemporaryFile',
        return_value=mock_object(name='tmp_file')
        )
    @patch('data_pipeline.management.commands.apply_fixtures.call_command')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.BlockBlobService',
        return_value=Mock(
            get_blob_to_path=mock_get_blob_to_path,
            list_blobs=Mock(return_value=[mock_object(name='001_investigator')]))
    )
    def test_apply_fixtures(self, patched_block_blob_service, patched_call_command, _, __):
        expect(AppliedFixture.objects.count()).to.eq(0)
        call_command('apply_fixtures')
        mock_get_blob_to_path.assert_called_with('fixtures', '001_investigator', 'tmp_file')
        patched_call_command.assert_called_with('loaddata', 'tmp_file')
        applied_fixture = AppliedFixture.objects.first()
        expect(applied_fixture.id).to.eq(1)
        expect(applied_fixture.file_name).to.eq('001_investigator')

    @patch('data_pipeline.management.commands.apply_fixtures.os.remove')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.NamedTemporaryFile',
        return_value=mock_object(name='tmp_file')
        )
    @patch('data_pipeline.management.commands.apply_fixtures.call_command')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.BlockBlobService',
        return_value=Mock(
            get_blob_to_path=mock_get_blob_to_path,
            list_blobs=Mock(return_value=[
                mock_object(name=file_name)
                for file_name in ['001_investigator', '002_allegation', '003_investigatorallegation']
            ])
        )
    )
    def test_no_apply_old_fixtures(self, patched_block_blob_service, patched_call_command, _, __):
        AppliedFixtureFactory(id=1)
        expect(AppliedFixture.objects.count()).to.eq(1)
        call_command('apply_fixtures')
        mock_get_blob_to_path.assert_has_calls([
            call('fixtures', '002_allegation', 'tmp_file'),
            call('fixtures', '003_investigatorallegation', 'tmp_file')
            ])
        patched_call_command.to.be.called_with('loaddata', 'tmp_file')
        expect(AppliedFixture.objects.count()).to.eq(3)

    @patch('data_pipeline.management.commands.apply_fixtures.os.remove')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.NamedTemporaryFile',
        return_value=mock_object(name='tmp_file')
        )
    @patch('data_pipeline.management.commands.apply_fixtures.call_command')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.BlockBlobService',
        return_value=Mock(
            get_blob_to_path=mock_get_blob_to_path,
            list_blobs=Mock(return_value=[
                mock_object(name=file_name)
                for file_name in ['001_investigator', '002_allegation', 'WIP_003_investigatorallegation']
            ])
        )
    )
    def test_no_apply_WIP_fixtures(self, patched_block_blob_service, patched_call_command, _, __):
        expect(AppliedFixture.objects.count()).to.eq(0)
        call_command('apply_fixtures')
        mock_get_blob_to_path.assert_has_calls([
            call('fixtures', '001_investigator', 'tmp_file'),
            call('fixtures', '002_allegation', 'tmp_file')
            ])
        patched_call_command.to.be.called_with('loaddata', 'tmp_file')
        expect(AppliedFixture.objects.count()).to.eq(2)

    @patch('data_pipeline.management.commands.apply_fixtures.os.remove')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.NamedTemporaryFile',
        return_value=mock_object(name='tmp_file')
        )
    @patch('data_pipeline.management.commands.apply_fixtures.call_command')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.BlockBlobService',
        return_value=Mock(
            get_blob_to_path=mock_get_blob_to_path,
            list_blobs=Mock(return_value=[mock_object(name='001_investigator')]))
    )
    def test_handle_command_error_gracefully(self, _, patched_call_command, __, ___):
        patched_call_command.side_effect = CommandError('Format not right')
        call_command('apply_fixtures')
        mock_get_blob_to_path.to.be.called_with('fixtures', '001_investigator', 'tmp_file')
        patched_call_command.to.be.called_with('loaddata', 'tmp_file')
        expect(AppliedFixture.objects.count()).to.eq(0)
