import pandas as pd
from robber import expect
from mock import Mock

from django.test import SimpleTestCase

from data_importer.base.analyzers import (
    ProfileCategorizer, LinkableAnalyzer, LinkableAnalysis, build_error_map
)


class ProfileCategorizerTestCase(SimpleTestCase):
    def setUp(self):
        linkable_analyzer = Mock()
        linkable_analyzer.analyze = Mock()
        profile_categorizer = ProfileCategorizer(linkable_analyzer)
        analysis = Mock()
        linkable_analyzer.analyze = Mock(return_value=analysis)

        self.profile_categorizer = profile_categorizer
        self.analysis = analysis

    def test_categorize_new(self):
        self.analysis.has_only_one_confident = True
        expect(self.profile_categorizer.categorize(Mock())).to.be.eq('New')

    def test_categorize_high_confidence(self):
        self.analysis.has_no_linkables = False
        self.analysis.has_only_one_confident = True
        expect(self.profile_categorizer.categorize(Mock())).to.be.eq('HighConfidence')

    def test_categorize_single_low_confidence(self):
        self.analysis.has_no_linkables = False
        self.analysis.has_only_one_confident = False
        self.analysis.has_only_one_linkable = True
        expect(self.profile_categorizer.categorize(Mock())).to.be.eq('SingleLowConfidence')

    def test_categorize_multiple_high_confidence_and_unmatchable(self):
        self.analysis.has_no_linkables = False
        self.analysis.has_only_one_confident = False
        self.analysis.has_only_one_linkable = False
        expect(self.profile_categorizer.categorize(Mock())).to.be.eq('MultipleHighConfidence/Unmatchable')


class LinkableAnalyzerTestCase(SimpleTestCase):
    def test_analyze(self):
        might_be_linkable = Mock()
        linkable_searcher = Mock()
        linkable_searcher.search = Mock(return_value=pd.DataFrame.from_dict([might_be_linkable]))
        similarity_computer = Mock()
        similarity_computer.compute = Mock(return_value=(None, .8))
        linkable_analyzer = LinkableAnalyzer(.7, .4, linkable_searcher, similarity_computer)
        analysis = linkable_analyzer.analyze(Mock())

        expect(analysis).to.be.instanceof(LinkableAnalysis)
        expect(len(analysis.confidents)).to.be.eq(1)
        expect(len(analysis.linkables)).to.be.eq(1)


class LinkableAnalysisTestCase(SimpleTestCase):
    def test_has_no_linkables(self):
        expect(LinkableAnalysis([], []).has_no_linkables).to.be.true()

    def test_has_only_one_confident(self):
        expect(LinkableAnalysis([1], [1]).has_only_one_confident).to.be.true()

    def test_has_only_one_linkable(self):
        expect(LinkableAnalysis([], [1]).has_only_one_linkable).to.be.true()

    def test_best(self):
        expect(LinkableAnalysis([1], [1]).best).to.be.eq(1)
        expect(LinkableAnalysis([], [1]).best).to.be.none()


class AnalyzersTestCase(SimpleTestCase):
    def test_build_error_map(self):
        merger = Mock()
        profile = Mock()
        profile.name = '1'
        candidate = Mock()
        merger.check_mergeable = Mock(return_value=(None, [('key', 1, 2, )],))
        result = build_error_map(merger, profile, candidate)
        expect(result).to.be.eq([{
            'key': 'key',
            'profile_attribute': 1,
            'candidate_attribute': 2,
            'idx': '1'
        }])
