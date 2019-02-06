from data.models import OfficerAllegation, PoliceWitness, Victim, Area
from xlsx.constants import INVESTIGATOR_XLSX
from xlsx.serializers.area_xlsx_serializer import AreaXlsxSerializer
from xlsx.serializers.officer_allegation_xlsx_serializer import (
    OfficerAllegationXlsxSerializer,
    OfficerFromAllegationOfficerXlsxSerializer,
)
from xlsx.serializers.police_witness_xlsx_serializer import PoliceWitnessXlsxSerializer
from xlsx.serializers.victim_xlsx_serializer import VictimXlsxSerializer
from xlsx.writers.officer_xlsx_writer import OfficerXlsxWriter


class InvestigatorXlsxWriter(OfficerXlsxWriter):
    file_name = INVESTIGATOR_XLSX

    def write_allegation_sheet(self):
        ws = self.wb.create_sheet('Allegation', 0)
        officer_allegations = OfficerAllegation.objects.filter(
            allegation__investigatorallegation__investigator__officer=self.officer
        ).distinct().select_related('allegation').order_by('allegation__crid')
        self.write_sheet(ws, officer_allegations, OfficerAllegationXlsxSerializer)

    def write_accused_officers_sheet(self):
        ws = self.wb.create_sheet('Accused Officer', 1)
        officer_allegations = OfficerAllegation.objects.filter(
            allegation__investigatorallegation__investigator__officer=self.officer
        ).distinct().select_related('allegation').order_by('allegation__crid')
        self.write_sheet(ws, officer_allegations, OfficerFromAllegationOfficerXlsxSerializer)

    def write_police_witnesses_sheet(self):
        ws = self.wb.create_sheet('Police Witness', 2)
        police_witnesses = PoliceWitness.objects.filter(
            allegation__investigatorallegation__investigator__officer=self.officer
        ).distinct().select_related('officer', 'allegation').order_by('allegation__crid')
        self.write_sheet(ws, police_witnesses, PoliceWitnessXlsxSerializer)

    def write_beat_sheet(self):
        ws = self.wb.create_sheet('Beat', 3)
        beats = Area.objects.filter(
            beats__investigatorallegation__investigator__officer=self.officer
        ).distinct().select_related('police_hq').order_by('id')
        self.write_sheet(ws, beats, AreaXlsxSerializer)

    def write_victim_sheet(self):
        ws = self.wb.create_sheet('Victim', 4)
        victims = Victim.objects.filter(
            allegation__investigatorallegation__investigator__officer=self.officer
        ).select_related('allegation').order_by('allegation__crid')
        self.write_sheet(ws, victims, VictimXlsxSerializer)

    def export_xlsx(self):
        self.write_allegation_sheet()
        self.write_accused_officers_sheet()
        self.write_police_witnesses_sheet()
        self.write_beat_sheet()
        self.write_victim_sheet()
        self.save()
