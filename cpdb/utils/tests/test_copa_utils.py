from django.test import TestCase

from robber import expect

from utils.copa_utils import extract_copa_executive_summary


class CopaUtilsTestCase(TestCase):
    def test_extract_copa_executive_summary(self):
        text_content = (
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nSUMMARY REPORT OF INVESTIGATION1'
            '\nI. EXECUTIVE SUMMARY'
            '\nDate of Incident: September 25, 2015'
            '\nTime of Incident: 8:53 pm.'
            '\nLocation of Incident: N. Central Park Avenue, Chicago, IL'
            '\nDate of COPA Notification: September 25, 2015'
            '\nTime of COPA Notification: 9:15 pm.'
            '\nOn September 25, 2015, at approximately 8:50 pm, Officers A and responded to a'
            '\ncall of a disturbance with a mentally ill subject, Involved Civilian 1 (Involved Civilian 1), at '
            '\nN. Central Park Avenue, Chicago, IL. Upon arrival, the officers met with Involved Civilian'
            '\nmother, Involved Civilian 2 (Involved Civilian 2), who stated that Involved Civilian 1 was acting'
            '\ncrazy, had a knife, and would not come out of his bedroom.'
            '\nII. INVOLVED PARTIES'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nAssignment: XX, DOB: 1983, Male White.'
            '\nInvolved Individual#1: Involved Civilian 1, DOB: 1982, Male, Black.'
            '\n1 On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            'On September 25, 2015, at approximately 8:50 pm, Officers A and responded to a '
            'call of a disturbance with a mentally ill subject, Involved Civilian 1 (Involved Civilian 1), at '
            'N. Central Park Avenue, Chicago, IL. Upon arrival, the officers met with Involved Civilian '
            'mother, Involved Civilian 2 (Involved Civilian 2), who stated that Involved Civilian 1 was acting '
            'crazy, had a knife, and would not come out of his bedroom.'
        )

    def test_extract_executive_summary_of_incident_pattern_from_copa_attachment(self):
        text_content = (
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nSUMMARY REPORT OF INVESTIGATION1'
            '\nSUMMARY OF INCIDENT'
            '\nOn September 25, 2015, at approximately 8:50 pm, Officers A and responded to a'
            '\ncall of a disturbance with a mentally ill subject, Involved Civilian 1 (Involved Civilian 1), at '
            '\nN. Central Park Avenue, Chicago, IL. Upon arrival, the officers met with Involved Civilian'
            '\nmother, Involved Civilian 2 (Involved Civilian 2), who stated that Involved Civilian 1 was acting'
            '\ncrazy, had a knife, and would not come out of his bedroom.'
            '\nINVESTIGATION'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\n1 On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            'On September 25, 2015, at approximately 8:50 pm, Officers A and responded to a '
            'call of a disturbance with a mentally ill subject, Involved Civilian 1 (Involved Civilian 1), at '
            'N. Central Park Avenue, Chicago, IL. Upon arrival, the officers met with Involved Civilian '
            'mother, Involved Civilian 2 (Involved Civilian 2), who stated that Involved Civilian 1 was acting '
            'crazy, had a knife, and would not come out of his bedroom.'
        )

    def test_extract_executive_summary_introduction_pattern_from_copa_attachment(self):
        text_content = (
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nSUMMARY OF INCIDENT'
            '\nOn September 25, 2015, at approximately 8:50 pm, Officers A and responded to a'
            '\ncall of a disturbance with a mentally ill subject, Involved Civilian 1 (Involved Civilian 1), at '
            '\nN. Central Park Avenue, Chicago, IL. Upon arrival, the officers met with Involved Civilian'
            '\nmother, Involved Civilian 2 (Involved Civilian 2), who stated that Involved Civilian 1 was acting'
            '\ncrazy, had a knife, and would not come out of his bedroom.'
            '\nALLEGATIONS'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nINVESTIGATION'
            '\n1 On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            'On September 25, 2015, at approximately 8:50 pm, Officers A and responded to a '
            'call of a disturbance with a mentally ill subject, Involved Civilian 1 (Involved Civilian 1), at '
            'N. Central Park Avenue, Chicago, IL. Upon arrival, the officers met with Involved Civilian '
            'mother, Involved Civilian 2 (Involved Civilian 2), who stated that Involved Civilian 1 was acting '
            'crazy, had a knife, and would not come out of his bedroom.'
        )

    def test_extract_copa_executive_summary_with_exact_before_text_from_copa_attachment(self):
        text_content = (
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nINTRODUCTION'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nINVESTIGATION'
            '\n1 On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            'Involved Officer Officer A, star Employee Date of '
            'Appointment: Chicago Police Officer, Unit of'
        )

    def test_extract_copa_executive_summary_with_exclude_text(self):
        text_content = (
            '\nINTRODUCTION'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nCIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nINVESTIGATION'
            '\n1 On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            'Involved Officer Officer A, star Employee Date of '
            'Appointment: Chicago Police Officer, Unit of'
        )

    def test_extract_copa_executive_summary_with_date_time_text(self):
        text_content = (
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nINVESTIGATION'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nDate of IPRA'
            '\n10:12 PM'
            '\nOn September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
            '\nII. INVOLVED PARTIES'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nAssignment: XX, DOB: 1983, Male White.'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            '10:12 PM '
            'On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            'Independent Police'
        )

    def test_extract_copa_executive_summary_with_summary_title(self):
        text_content = (
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nINVESTIGATION'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nSUMMARY OF INCIDENT'
            '\nOn September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
            '\nII. INVOLVED PARTIES'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nAssignment: XX, DOB: 1983, Male White.'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            'On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            'Independent Police'
        )

    def test_extract_copa_executive_summary_with_summary_title_end_with_colon(self):
        text_content = (
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nINVESTIGATION'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nSummary of incident:'
            '\nOn September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
            '\nII. INVOLVED PARTIES'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nAssignment: XX, DOB: 1983, Male White.'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            'On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            'Independent Police'
        )

    def test_extract_copa_executive_summary_with_exact_summary_title(self):
        text_content = (
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nINVESTIGATION'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nSUMMARY OF'
            '\nOn September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
            '\nII. INVOLVED PARTIES'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nAssignment: XX, DOB: 1983, Male White.'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            'On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            'Independent Police'
        )

    def test_extract_copa_executive_summary_with_exact_summary_title_end_with_colon(self):
        text_content = (
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nINVESTIGATION'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nSummary of:'
            '\nOn September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
            '\nII. INVOLVED PARTIES'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nAssignment: XX, DOB: 1983, Male White.'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            'On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            'Independent Police'
        )

    def test_extract_copa_executive_summary_with_alternative_title(self):
        text_content = (
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY '
            '\nINVESTIGATION'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nTime of COPA'
            '\nOn September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            '\nIndependent Police'
            '\nThis is an alternative title:'
            '\nInvolved Officer Officer A, star Employee Date of'
            '\nAppointment: Chicago Police Officer, Unit of'
            '\nAssignment: XX, DOB: 1983, Male White.'
        )

        expect(extract_copa_executive_summary(text_content)).to.eq(
            'On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the '
            'Independent Police'
        )

    def test_can_not_extract_copa_executive_summary(self):
        text_content = 'This is invalid text content.'

        expect(extract_copa_executive_summary(text_content)).to.be.none()
