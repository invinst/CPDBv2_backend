import pandas as pd

from data_importer.base.utils.wrap import wrap


class Rule(object):
    pass


class SimpleRule(Rule):
    NAME = 'SimpleRule'

    @staticmethod
    def apply(profile_attribute, candidate_attribute):
        if any([pd.isnull(profile_attribute), pd.isnull(candidate_attribute)]):
            return True, (profile_attribute or candidate_attribute)

        if profile_attribute == candidate_attribute:
            return True, candidate_attribute
        else:
            return False, None

    @staticmethod
    def resolve(profile_attribute, candidate_attribute, merged_attribute):
        if candidate_attribute != merged_attribute:
            return merged_attribute


class SetRule(Rule):
    NAME = 'SetRule'

    @staticmethod
    def apply(profile_attribute, candidate_attribute):
        profile_attribute = wrap(profile_attribute)
        candidate_attribute = wrap(candidate_attribute)

        return True, list(set(profile_attribute) | set(candidate_attribute))

    @staticmethod
    def resolve(profile_attribute, candidate_attribute, merged_attribute):
        differences = list(set(merged_attribute) - set(wrap(candidate_attribute)))

        if len(differences) > 0:
            return differences


class Merger(object):
    def __init__(self, schema=None, profile_prefix=''):
        self.schema = schema or {}
        self.profile_prefix = profile_prefix

    # TODO: Cache
    def check_mergeable(self, profile, candidate):
        changes = {}
        errors = []

        for key, rule in self.schema.items():
            profile_key = '{profile_prefix}{key}'.format(profile_prefix=self.profile_prefix, key=key)
            profile_attribute = profile[profile_key]
            candidate_attribute = candidate[key]
            success, merged_attribute = rule.apply(profile_attribute, candidate_attribute)

            if success:
                change = rule.resolve(profile_attribute, candidate_attribute, merged_attribute)
                if change is not None:
                    changes[key] = change

            else:
                errors.append((key, profile_attribute, candidate_attribute,))

        return changes, errors

    def is_mergeable(self, profile, candidate):
        _, errors = self.check_mergeable(profile, candidate)
        return len(errors) == 0
