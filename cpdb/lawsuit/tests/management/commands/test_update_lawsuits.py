from django.core.management import call_command
from django.test import TestCase

from mock import patch, Mock
from robber import expect

from lawsuit.management.commands.update_lawsuits import logger


class UpdateLawsuitsTestCase(TestCase):
    @patch('lawsuit.management.commands.update_lawsuits.LawsuitImporter')
    def test_update_lawsuits(self, LawsuitImporterMock):
        importer = Mock()
        LawsuitImporterMock.return_value = importer

        call_command('update_lawsuits')

        expect(LawsuitImporterMock).to.called_with(
            logger,
            force_update=False
        )
        expect(importer.update_data).to.be.called()

    @patch('lawsuit.management.commands.update_lawsuits.LawsuitImporter')
    def test_force_update_lawsuits(self, LawsuitImporterMock):
        importer = Mock()
        LawsuitImporterMock.return_value = importer

        call_command('update_lawsuits', '--force')

        expect(LawsuitImporterMock).to.called_with(
            logger,
            force_update=True
        )

        expect(importer.update_data).to.be.called()
