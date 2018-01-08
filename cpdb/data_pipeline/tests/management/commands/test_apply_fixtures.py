from django.test import TestCase
from django.core.management import call_command

from mock import patch, call
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


class ApplyFixturesCommandTestCase(TestCase):
    @patch('data_pipeline.management.commands.apply_fixtures.os.remove')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.NamedTemporaryFile',
        return_value=mock_object(name='tmp_file')
        )
    @patch('data_pipeline.management.commands.apply_fixtures.call_command')
    @patch('data_pipeline.management.commands.apply_fixtures.BlockBlobService.get_blob_to_path')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.BlockBlobService.list_blobs',
        return_value=[mock_object(name='001_investigator')])
    def test_apply_fixtures(self, patched_list_blobs, patched_get_blob_to_path, patched_call_command, _, __):
        expect(AppliedFixture.objects.count()).to.eq(0)
        call_command('apply_fixtures')
        patched_get_blob_to_path.assert_called_with('fixtures', '001_investigator', 'tmp_file')
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
    @patch('data_pipeline.management.commands.apply_fixtures.BlockBlobService.get_blob_to_path')
    @patch(
        'data_pipeline.management.commands.apply_fixtures.BlockBlobService.list_blobs',
        return_value=[
            mock_object(name=file_name)
            for file_name in ['001_investigator', '002_allegation', '003_investigatorallegation']
        ])
    def test_no_apply_old_fixtures(self, patched_list_blobs, patched_get_blob_to_path, patched_call_command, _, __):
        AppliedFixtureFactory(id=1)
        expect(AppliedFixture.objects.count()).to.eq(1)
        call_command('apply_fixtures')
        patched_get_blob_to_path.assert_has_calls([
            call('fixtures', '002_allegation', 'tmp_file'),
            call('fixtures', '003_investigatorallegation', 'tmp_file')
            ])
        patched_call_command.assert_called_with('loaddata', 'tmp_file')
        expect(AppliedFixture.objects.count()).to.eq(3)
