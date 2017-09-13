import json
import itertools

from data.models import Officer, OfficerAllegation


class OfficerSocialGraphVisualTokenRenderer:
    script_path = 'officer_social_graph_visual_token_renderer.js'

    def coaccusals_between_two_officers(self, officer1, officer2):
        return OfficerAllegation.objects.filter(officer=officer1).filter(
            allegation__officerallegation__officer=officer2).order_by('allegation').distinct('allegation').count()

    def serialize(self, officer):
        coaccused = Officer.objects.filter(
            officerallegation__allegation__officerallegation__officer=officer
        ).distinct()
        coaccused = sorted(coaccused, key=lambda obj: obj.id)
        if not coaccused:
            coaccused = [officer]

        coaccusals = [
            {
                'source': o1.id,
                'target': o2.id,
                'crs': self.coaccusals_between_two_officers(o1, o2)
            }
            for o1, o2 in itertools.combinations(coaccused, 2)]
        coaccusals = filter(lambda o: o['crs'] > 0, coaccusals)

        return json.dumps({
            'focusedId': officer.id,
            'nodes': [
                {
                    'crs': o.allegation_count,
                    'trrs': 0,
                    'salary': 0,
                    'id': o.id,
                    'name': o.full_name
                }
                for o in coaccused],
            'links': coaccusals
        })

    def blob_name(self, officer):
        return 'officer_%s' % officer.id
