import pandas as pd
from jellyfish import jaro_distance

from data_importer.base.utils.wrap import wrap


class Rule(object):
    pass


class Any(Rule):
    def __init__(self, *args, **kwargs):
        self.rules = args

    def apply(self, this, that):
        return any([rule.apply(this, that) for rule in self.rules])


class All(Rule):
    def __init__(self, *args, **kwargs):
        self.rules = args

    def apply(self, this, that):
        return all([rule.apply(this, that) for rule in self.rules])


class Intersected(Rule):
    @staticmethod
    def apply(this, that):
        this = wrap(this)
        that = wrap(that)

        return len(set(this) & set(that)) >= 1


class EitherNone(Rule):
    @staticmethod
    def apply(this, that):
        return any([pd.isnull(this), pd.isnull(that)])


class Equal(Rule):
    @staticmethod
    def apply(this, that):
        return this == that


class Similar(object):
    def __init__(self, method='jaro', threshold=0.5):
        self.method = method
        self.threshold = threshold

    @property
    def _distance_method(self):
        return {
            'jaro': jaro_distance
        }[self.method]

    def apply(self, this, that):
        return self._distance_method(unicode(this), unicode(that)) >= self.threshold


class SimilarityComputer(object):
    DEFAULT_RULE = Any(EitherNone, Equal)

    def __init__(self, profile_prefix='', weights=None, instructions=None, excludes=None):
        self.weights = weights or {}
        self.excludes = excludes or []
        self.instructions = instructions or {}
        self.profile_prefix = profile_prefix

    def compute(self, profile, candidate):
        total = 0
        total_weight = sum([float(v) for k, v in self.weights.items() if k not in self.excludes])
        violations = []

        for key in self.weights:
            if key not in self.excludes:
                profile_key = '{profile_prefix}{key}'.format(profile_prefix=self.profile_prefix, key=key)
                profile_attribute = profile[profile_key]
                candidate_attribute = candidate[key]
                instruction = self.instructions.get(key, self.DEFAULT_RULE)

                if instruction.apply(profile_attribute, candidate_attribute):
                    total += self.weights[key]
                else:
                    violations.append((key, profile_attribute, candidate_attribute,))

        return violations, total / total_weight
