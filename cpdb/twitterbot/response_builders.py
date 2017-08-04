import random
import itertools

from django.conf import settings
from django.template import Context, Template

from .models import ResponseTemplate
from data.models import Allegation


class BaseResponseBuilder:
    def build(self, entities=None, extra_variables=None, context=None):
        response_templates = ResponseTemplate.objects.filter(response_type=self.response_type)
        for variables_set in self.get_variables_sets(entities, context):
            if extra_variables:
                variables_set.update(extra_variables)
            response_template = random.choice(response_templates)
            if context is not None:
                context.setdefault('responses_count', 0)
                context['responses_count'] += 1
            source = variables_set.get('source', ())
            url = variables_set.get('url', '')
            yield (source, Template(response_template.syntax).render(Context(variables_set)), url)


class SingleOfficerResponseBuilder(BaseResponseBuilder):
    response_type = 'single_officer'

    def get_variables_sets(self, entities, context):
        for (source, officer) in entities:
            yield {
                'officer': officer,
                'url': '%s%s' % (settings.DOMAIN, officer.get_absolute_url()),
                'source': (source, )
            }


class CoaccusedPairResponseBuilder(BaseResponseBuilder):
    response_type = 'coaccused_pair'

    def get_variables_sets(self, entities, context):
        for (source1, officer1), (source2, officer2) in itertools.combinations(entities, 2):
            coaccused = Allegation.objects.filter(officerallegation__officer=officer1)\
                .filter(officerallegation__officer=officer2).distinct().count()
            if coaccused > 0:
                yield {
                    'officer1': officer1,
                    'officer2': officer2,
                    'coaccused': coaccused,
                    'source': (source1, source2)
                }


class NotFoundResponseBuilder(BaseResponseBuilder):
    response_type = 'not_found'

    def get_variables_sets(self, entities, context):
        if context is not None and context.get('responses_count', 0) == 0:
            yield {}
