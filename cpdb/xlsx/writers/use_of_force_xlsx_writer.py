from trr.models import TRR
from xlsx.serializers.trr_xlsx_serializer import TRRXlsxSerializer
from xlsx.writers.officer_xlsx_writer import OfficerXlsxWriter


class UseOfForceXlsxWriter(OfficerXlsxWriter):
    @property
    def file_name(self):
        return f'use_of_force_{self.officer.id}.xlsx'

    def export_xlsx(self):
        ws = self.wb.create_sheet('Allegation', 0)
        trrs = TRR.objects.filter(
            officer=self.officer
        ).select_related('officer_unit', 'officer_unit_detail').order_by('id')
        rows = TRRXlsxSerializer(trrs, many=True).data
        self.write_sheet(ws, rows)
        self.save()
