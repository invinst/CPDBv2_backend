class LinkableSearcher(object):
    DEFAULT_STRATEGY = 'SAME_NAME'

    def __init__(self, df_officers, strategy=None):
        self.df_officers = df_officers
        self.strategy = strategy or self.DEFAULT_STRATEGY

    def _search_by_same_name(self, profile):
        return self.df_officers[(self.df_officers['first_name'] == profile['first_name']) &
                                (self.df_officers['last_name'] == profile['last_name'])]

    def _search_by_marriage(self, profile):
        return self.df_officers[(self.df_officers['first_name'] == profile['first_name']) &
                                (self.df_officers['gender'] == 'F')]

    def search(self, profile):
        return {
            'SAME_NAME': self._search_by_same_name,
            'MARRIAGE': self._search_by_marriage
        }[self.strategy](profile)


class PoliceUnitLinkableSearcher(object):
    def __init__(self, police_units, profile_prefix=''):
        self.police_units = police_units
        self.profile_prefix = profile_prefix

    def search(self, row):
        return self.police_units[
            self.police_units['unit_name'] == row['{prefix}unit_name'.format(prefix=self.profile_prefix)]]
