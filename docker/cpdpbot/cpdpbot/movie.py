import moviepy.editor as mpy

from .figures import ChartFigure


PERCENTILE_KEYS = [
    'percentile_allegation_civilian', 'percentile_allegation_internal', 'percentile_trr'
]


def has_enough_data(data):
    vals = [
        data.get(key, None)
        for key in PERCENTILE_KEYS
    ]
    vals = [
        val for val in vals if val is not None
    ]
    return len(vals) == 3


def tween(matrix, begin_ind, key, time_ratio):
    return matrix[begin_ind][key] + (matrix[begin_ind + 1][key] - matrix[begin_ind][key]) * time_ratio


def draw_frame(data, duration):
    def draw(time):
        def make_frame():
            if len(data) == 1:
                return data[0]

            year_duration_length = duration / (len(data) - 1)
            begin_ind = int(time / year_duration_length)
            time_ratio = (time - year_duration_length * begin_ind) / year_duration_length
            return [
                tween(data, begin_ind, key, time_ratio)
                for key in PERCENTILE_KEYS
            ]

        chart = ChartFigure(640, 640)
        return chart.draw(*(make_frame())).get_npimage()

    return draw


def write_mp4(data, yd, fps):
    filename = '/tmp/%s.mp4' % data['id']

    percentiles = [
        {
            key: float(year[key])
            for key in PERCENTILE_KEYS
        }
        for year in data['percentiles']
        if has_enough_data(year)
    ]

    duration = yd * (len(percentiles) - 1)
    clip = mpy.VideoClip(
        draw_frame(percentiles, duration),
        duration=duration
    )
    clip.write_videofile(filename, fps=fps)
    return filename
