from visual_token.figures import ChartFigure


def make_draw_frame(data, duration):
    def draw_frame(t):
        def data_at_time(data, movie_length, time):
            if len(data) == 1:
                return data[0]

            value_keys = ['percentile_allegation_civilian', 'percentile_allegation_internal', 'percentile_trr']

            year_duration_length = movie_length / (len(data) - 1)
            i_from = int(time / year_duration_length)
            time_within_gap = (time - year_duration_length * i_from) / year_duration_length
            return [
                data[i_from][key] + (data[i_from + 1][key] - data[i_from][key]) * time_within_gap
                for key in value_keys
            ]

        data_at_time = data_at_time(data, duration, t)
        chart = ChartFigure(640, 640)
        return chart.draw(data_at_time).get_npimage()

    return draw_frame
