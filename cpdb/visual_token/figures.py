import math

import cairo


def scale_percentile(val):
        return int((val - 0.0001) / 20) + 1 if val != 0 else 0


def get_visual_token_oig_background(civil_percentile, internal_percentile, use_of_force_percentile):
    OIG_VISUAL_TOKEN_COLOR_SCHEME = {
        '30': (0.976, 0.58, 0.42), '53': (0.957, 0.176, 0.122), '34': (1.0, 0.314, 0.314), '04': (0.949, 0.502, 0.506),
        '02': (0.965, 0.788, 0.816), '03': (0.965, 0.659, 0.655), '00': (0.961, 0.957, 0.957),
        '01': (0.988, 0.878, 0.878), '20': (0.961, 0.773, 0.635), '21': (0.953, 0.69, 0.58),
        '22': (0.957, 0.635, 0.596), '05': (0.937, 0.435, 0.439), '44': (0.953, 0.165, 0.161),
        '45': (0.863, 0.173, 0.188), '42': (0.953, 0.361, 0.09), '43': (0.953, 0.263, 0.224),
        '40': (0.984, 0.439, 0.271), '41': (0.988, 0.365, 0.173), '24': (0.933, 0.392, 0.396),
        '25': (0.91, 0.314, 0.314), '11': (0.976, 0.827, 0.765), '10': (0.976, 0.871, 0.78),
        '13': (0.953, 0.624, 0.557), '12': (0.953, 0.678, 0.678), '15': (0.929, 0.38, 0.329),
        '14': (0.945, 0.502, 0.459), '33': (0.992, 0.369, 0.298), '32': (0.929, 0.455, 0.404),
        '31': (0.973, 0.522, 0.404), '23': (0.949, 0.525, 0.529), '51': (1.0, 0.31, 0.075),
        '50': (0.976, 0.318, 0.145), '35': (0.925, 0.204, 0.208), '52': (0.965, 0.251, 0.086),
        '55': (0.961, 0.145, 0.141), '54': (0.941, 0.125, 0.118)
    }
    OIG_EXTRA_BLUE_COLOR_SCHEME = {
        '1': (0.867, 0.902, 0.969), '0': (0.961, 0.957, 0.957), '3': (0.741, 0.78, 0.925),
        '2': (0.82, 0.867, 0.945), '5': (0.251, 0.369, 0.765), '4': (0.518, 0.596, 0.847)
    }

    key = ''.join([
        str(scale_percentile(civil_percentile)),
        str(scale_percentile(use_of_force_percentile))
    ])
    return OIG_VISUAL_TOKEN_COLOR_SCHEME[key]\
        if key != '00'\
        else OIG_EXTRA_BLUE_COLOR_SCHEME[str(scale_percentile(internal_percentile))]


def draw_frame(data, frame_count, frame_num, width, height):
    def data_at_frame(data, time):
        total_frames = float(frame_count)
        keys = ['percentile_allegation_civilian', 'percentile_allegation_internal', 'percentile_trr']
        gap_length = total_frames / (len(data) - 1) if len(data) > 1 else total_frames
        i_from = int(time / gap_length)
        time_within_gap = (time - gap_length * i_from) / gap_length
        return [
            data[i_from][key] + (data[i_from + 1][key] - data[i_from][key]) * time_within_gap
            for key in keys
        ]

    def draw_triangle(lengths):
        ctx.move_to(center_x - lengths[0] * math.sin(math.pi/3), center_y - lengths[0] * math.cos(math.pi/3))
        ctx.line_to(center_x + lengths[1] * math.sin(math.pi/3), center_y - lengths[1] * math.cos(math.pi/3))
        ctx.line_to(center_x, center_y + lengths[2])
        ctx.close_path()

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    data_at_frame = data_at_frame(data, frame_num)
    center_x = width / 2
    center_y = height / 2
    spine_length = 200

    # Fill background
    ctx.rectangle(0, 0, width, height)
    background_color = get_visual_token_oig_background(*data_at_frame)
    ctx.set_source_rgb(*background_color)
    ctx.fill()

    # Draw chart triangle
    draw_triangle([spine_length] * 3)
    ctx.set_source_rgba(1, 1, 1, 0.6)
    ctx.fill()

    # Draw chart data
    draw_triangle([value * spine_length / 100 for value in data_at_frame])
    ctx.set_source_rgb(0.137, 0.121, 0.125)
    ctx.fill_preserve()
    ctx.stroke()

    # Draw chart grid
    num_of_grid_line = 4
    for i in range(num_of_grid_line):
        draw_triangle([(i + 1) * spine_length / (num_of_grid_line + 1)] * 3)
        ctx.set_source_rgba(*(background_color + (0.25,)))
        ctx.stroke()

    return surface
