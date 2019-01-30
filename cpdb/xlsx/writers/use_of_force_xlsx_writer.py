from trr.models import TRR
from xlsx.constants import USE_OF_FORCE_XSLX
from xlsx.serializers.trr_xlsx_serializer import TRRXlsxSerializer
from xlsx.writers.officer_xlsx_writer import OfficerXlsxWriter


class UseOfForceXlsxWriter(OfficerXlsxWriter):
    file_name = USE_OF_FORCE_XSLX

    def export_xlsx(self):
        ws = self.wb.create_sheet('Use Of Force', 0)
        trrs = TRR.objects.filter(
            officer=self.officer
        ).select_related('officer_unit', 'officer_unit_detail').order_by('id')
        self.write_sheet(ws, trrs, TRRXlsxSerializer)
        self.save()
