class ProfileCategorizer(object):
    def __init__(self, linkable_analyzer=None):
        self.linkable_analyzer = linkable_analyzer

    def categorize(self, profile):
        analysis = self.linkable_analyzer.analyze(profile)

        if analysis.has_no_linkables:
            return 'New'

        if analysis.has_only_one_confident:
            return 'HighConfidence'

        if analysis.has_only_one_linkable:
            return 'SingleLowConfidence'

        return 'MultipleHighConfidence/Unmatchable'


class LinkableAnalyzer(object):
    def __init__(self, high, low, linkable_searcher, similarity_computer):
        self.high = high
        self.low = low
        self.linkable_searcher = linkable_searcher
        self.similarity_computer = similarity_computer

    # TODO: This should be cached
    def analyze(self, row):
        might_be_linkables = self.linkable_searcher.search(row)
        confidents = []
        linkables = []

        for index, might_be_linkable in might_be_linkables.iterrows():
            _, score = self.similarity_computer.compute(row, might_be_linkable)

            if score >= self.high:
                confidents.append(might_be_linkable)

            if score >= self.low:
                linkables.append(might_be_linkable)

        return LinkableAnalysis(confidents, linkables)


class LinkableAnalysis(object):
    def __init__(self, confidents=None, linkables=None):
        self.confidents = confidents or []
        self.linkables = linkables or []

    @property
    def has_no_linkables(self):
        return len(self.linkables) == 0

    @property
    def has_only_one_confident(self):
        return len(self.confidents) == 1

    @property
    def has_only_one_linkable(self):
        return len(self.linkables) == 1

    @property
    def best(self):
        if len(self.confidents) > 0:
            return self.confidents[0]

        return None


def build_error_map(merger, profile, candidate):
    _, errors = merger.check_mergeable(profile, candidate)
    return [
        {
            'key': key,
            'profile_attribute': profile_attribute,
            'candidate_attribute': candidate_attribute,
            'idx': profile.name
        }
        for key, profile_attribute, candidate_attribute in errors
    ]
