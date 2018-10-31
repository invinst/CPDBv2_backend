import cProfile
import pstats
import StringIO
import re
import textwrap

from django.conf import settings
from django.http import HttpResponse


class ProfileMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def should_show_stats(self, request):
        is_superuser = hasattr(request, 'user') and request.user.is_superuser
        return 'prof' in request.GET and (settings.DEBUG or is_superuser)

    def __call__(self, request):
        if self.should_show_stats(request):       # pragma: no cover
            pr = cProfile.Profile()
            pr.enable()

            self.get_response(request)

            pr.disable()
            ps = pstats.Stats(pr).sort_stats('cumulative')
            formatter = ProfileStatsFormatter(
                ps, raw_records=200, group_records=50)

            response = HttpResponse(formatter.get_html())
        else:
            response = self.get_response(request)

        return response


class ProfileStatsFormatter(object):       # pragma: no cover
    """
    Helper for formatting profile stats to HTML with grouping
    """
    DEFAULT_SORTING = ('cumtime', 'calls')
    group_prefix_re = [
        re.compile("^.*/django/[^/]+"),
        re.compile("^(.*)/[^/]+$"),  # extract module path
        re.compile(".*"),  # catch strange entries
    ]

    def __init__(self, stats, sort_by=None, group_records=40, raw_records=100):
        self.total_time = 0
        self.time_by_file = {}
        self.time_by_group = {}
        self.num_of_group_records = group_records
        self.num_of_records = raw_records
        self.stats_str = self._get_stats_string(
            stats, sort_by=sort_by or self.DEFAULT_SORTING)
        # fill total_time, time_by_file, time_by_group fields
        self._preprocess_stats()

    @staticmethod
    def _get_stats_string(stats, sort_by):
        stats.stream = StringIO.StringIO()
        stats.sort_stats(*sort_by)
        stats.print_stats()
        return stats.stream.getvalue()

    def _preprocess_stats(self):
        for filename, time in self._iterate_records(self.stats_str):
            group = self._get_group(filename)
            self.time_by_group[group] = self.time_by_group.get(group, 0) + time
            self.time_by_file[filename] = self.time_by_file.get(filename, 0) + time
            self.total_time += time

    @staticmethod
    def _get_group(filename):
        for group_prefix in ProfileStatsFormatter.group_prefix_re:
            name = group_prefix.findall(filename)
            if name:
                return name[0]

    @staticmethod
    def _iterate_records(stats_str):
        # first 5 lines contains summary
        records = stats_str.split("\n")[5:]
        for record in records:
            fields = record.split()
            if len(fields) == 6:
                record_time = float(fields[1])
                filename = fields[5].split(":")[0]
                if filename:
                    yield filename, record_time

    def _get_summary(self, time_by_name):
        time_name = time_by_name.items()
        time_name.sort(reverse=True, key=lambda ((name, time)): time)
        res = "      tottime\n"
        for name, time in time_name[:self.num_of_group_records]:
            percent = 100 * time / self.total_time if self.total_time else 0
            res += "%4.1f%% %7.3f %s\n" % (percent, time, name)
        return res

    def get_html(self):
        raw_stats = '\n'.join(self.stats_str.split('\n')[:self.num_of_records])
        format_string = textwrap.dedent("""
            {raw_stats}

            ---- By filename ----

            {stats_by_filename}

            ---- By group ---

            {stats_by_group}
        """)
        return ("<pre >" + format_string + "</pre>").format(
            raw_stats=raw_stats,
            stats_by_filename=self._get_summary(self.time_by_file),
            stats_by_group=self._get_summary(self.time_by_group)
        )
