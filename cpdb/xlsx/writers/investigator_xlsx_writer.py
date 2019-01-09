from data.models import OfficerAllegation, InvestigatorAllegation, PoliceWitness, Victim, Area
from xlsx.serializers.area_xlsx_serializer import AreaXlsxSerializer
from xlsx.serializers.officer_allegation_xlsx_serializer import (
    OfficerAllegationXlsxSerializer,
    OfficerFromAllegationOfficerXlsxSerializer,
)
from xlsx.serializers.police_witness_xlsx_serializer import PoliceWitnessXlsxSerializer
from xlsx.serializers.victim_xlsx_serializer import VictimXlsxSerializer
from xlsx.writers.officer_xlsx_writer import OfficerXlsxWriter


class InvestigatorXlsxWriter(OfficerXlsxWriter):
    @property
    def file_name(self):
        return f'investigator_{self.officer.id}.xlsx'

    def write_allegation_sheet(self):
        ws = self.wb.create_sheet('Allegation', 0)
        officer_allegations = OfficerAllegation.objects.filter(
            allegation__investigatorallegation__investigator__officer=self.officer
        ).distinct().select_related('allegation').order_by('allegation__crid')
        rows = OfficerAllegationXlsxSerializer(officer_allegations, many=True).data
        self.write_sheet(ws, rows)

    def write_accused_officers_sheet(self):
        ws = self.wb.create_sheet('Accused Officer', 1)
        InvestigatorAllegation.objects.filter()
        officer_allegations = OfficerAllegation.objects.filter(
            allegation__investigatorallegation__investigator__officer=self.officer
        ).distinct().select_related('allegation').order_by('allegation__crid')
        rows = OfficerFromAllegationOfficerXlsxSerializer(officer_allegations, many=True).data
        self.write_sheet(ws, rows)

    def write_police_witnesses_sheet(self):
        ws = self.wb.create_sheet('Police Witness', 2)
        police_witnesses = PoliceWitness.objects.filter(
            allegation__investigatorallegation__investigator__officer=self.officer
        ).distinct().select_related('officer', 'allegation').order_by('allegation__crid')
        rows = PoliceWitnessXlsxSerializer(police_witnesses, many=True).data
        self.write_sheet(ws, rows)

    def write_beat_sheet(self):
        ws = self.wb.create_sheet('Beat', 3)
        beats = Area.objects.filter(
            beats__investigatorallegation__investigator__officer=self.officer
        ).distinct().select_related('police_hq').order_by('id')
        rows = AreaXlsxSerializer(beats, many=True).data
        self.write_sheet(ws, rows)

    def write_victim_sheet(self):
        ws = self.wb.create_sheet('Victim', 4)
        victims = Victim.objects.filter(
            allegation__investigatorallegation__investigator__officer=self.officer
        ).select_related('allegation').order_by('allegation__crid')
        rows = VictimXlsxSerializer(victims, many=True).data
        self.write_sheet(ws, rows)

    def export_xlsx(self):
        self.write_allegation_sheet()
        self.write_accused_officers_sheet()
        self.write_police_witnesses_sheet()
        self.write_beat_sheet()
        self.write_victim_sheet()
        self.save()
