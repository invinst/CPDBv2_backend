import itertools

from django.conf import settings
from django.template import Context, Template

from .models import TYPE_SINGLE_OFFICER, TYPE_COACCUSED_PAIR, TYPE_NOT_FOUND
from data.models import Allegation, Officer
from twitterbot.models import TweetResponseRoundRobin


class BaseResponseBuilder:
    def build(self, entities=None, extra_variables=None, context=None):
        for variables_set in self.get_variables_sets(entities, context):
            if extra_variables:
                variables_set.update(extra_variables)
            response_template = TweetResponseRoundRobin.objects.get_template(
                username=variables_set['user_name'], response_type=self.response_type)
            if context is not None:
                context.setdefault('responses_count', 0)
                context['responses_count'] += 1

            source = variables_set.get('source', ())
            url = variables_set.get('_url', '')
            entity = variables_set.get('_entity', None)
            officer1 = variables_set.get('officer1', None)
            officer2 = variables_set.get('officer2', None)
            coaccused = variables_set.get('coaccused', 0)

            tweet_content = Template(response_template.syntax).render(Context(variables_set))

            if len(tweet_content) > 140:
                tweet_content = tweet_content.replace('@{user_name} '.format(user_name=variables_set['user_name']), '')
            yield {
                'source': source,
                'tweet_content': tweet_content,
                'entity': entity,
                'url': url,
                'type': self.response_type,
                'officer1': officer1,
                'officer2': officer2,
                'coaccused': coaccused,
            }


class SingleOfficerResponseBuilder(BaseResponseBuilder):
    response_type = TYPE_SINGLE_OFFICER

    def get_variables_sets(self, entities, context):
        for (source, officer) in entities:
            yield {
                'officer': Officer.objects.get(pk=officer['id']),
                '_entity': officer,
                '_url': '%s%s' % (settings.DOMAIN, '/officer/%s/' % officer['id']),
                'source': (source, )
            }


class CoaccusedPairResponseBuilder(BaseResponseBuilder):
    response_type = TYPE_COACCUSED_PAIR

    def get_variables_sets(self, entities, context):
        for (source1, officer1), (source2, officer2) in itertools.combinations(entities, 2):
            coaccused = Allegation.objects.filter(officerallegation__officer_id=officer1['id'])\
                .filter(officerallegation__officer_id=officer2['id']).distinct().count()
            if coaccused > 0:
                yield {
                    'officer1': Officer.objects.get(pk=officer1['id']),
                    'officer2': Officer.objects.get(pk=officer2['id']),
                    'coaccused': coaccused,
                    'source': (source1, source2)
                }


class NotFoundResponseBuilder(BaseResponseBuilder):
    response_type = TYPE_NOT_FOUND

    def get_variables_sets(self, entities, context):
        try:
            tweet = context.get('incoming_tweet', None)
            if context.get('responses_count', 0) > 0:
                raise StopIteration()
            if tweet.is_retweet_of_twitterbot:
                raise StopIteration()
            if tweet.is_quoted_tweet_of_twitterbot:
                raise StopIteration()

        except AttributeError:
            raise StopIteration()
        yield {
            '_url': settings.DOMAIN
        }
