import math

import gizeh


class ChartFigure:  # pragma: no cover
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = gizeh.Surface(width, height)
        self.center = {'x': width / 2, 'y': height / 2}
        self.spine_length = 200

    def scale_percentile(self, val):
        return int((val - 0.0001) / 20) + 1 if val != 0 else 0

    def get_visual_token_oig_background(self, civil_percentile, internal_percentile, use_of_force_percentile):
        OIG_VISUAL_TOKEN_COLOR_SCHEME = {
            '30': (0.976, 0.58, 0.42), '53': (0.957, 0.176, 0.122), '34': (1.0, 0.314, 0.314),
            '04': (0.949, 0.502, 0.506), '02': (0.965, 0.788, 0.816), '03': (0.965, 0.659, 0.655),
            '00': (0.961, 0.957, 0.957), '01': (0.988, 0.878, 0.878), '20': (0.961, 0.773, 0.635),
            '21': (0.953, 0.69, 0.58), '22': (0.957, 0.635, 0.596), '05': (0.937, 0.435, 0.439),
            '44': (0.953, 0.165, 0.161), '45': (0.863, 0.173, 0.188), '42': (0.953, 0.361, 0.09),
            '43': (0.953, 0.263, 0.224), '40': (0.984, 0.439, 0.271), '41': (0.988, 0.365, 0.173),
            '24': (0.933, 0.392, 0.396), '25': (0.91, 0.314, 0.314), '11': (0.976, 0.827, 0.765),
            '10': (0.976, 0.871, 0.78), '13': (0.953, 0.624, 0.557), '12': (0.953, 0.678, 0.678),
            '15': (0.929, 0.38, 0.329), '14': (0.945, 0.502, 0.459), '33': (0.992, 0.369, 0.298),
            '32': (0.929, 0.455, 0.404), '31': (0.973, 0.522, 0.404), '23': (0.949, 0.525, 0.529),
            '51': (1.0, 0.31, 0.075), '50': (0.976, 0.318, 0.145), '35': (0.925, 0.204, 0.208),
            '52': (0.965, 0.251, 0.086), '55': (0.961, 0.145, 0.141), '54': (0.941, 0.125, 0.118)
        }
        OIG_EXTRA_BLUE_COLOR_SCHEME = {
            '1': (0.867, 0.902, 0.969), '0': (0.961, 0.957, 0.957), '3': (0.741, 0.78, 0.925),
            '2': (0.82, 0.867, 0.945), '5': (0.251, 0.369, 0.765), '4': (0.518, 0.596, 0.847)
        }

        key = ''.join([
            str(self.scale_percentile(civil_percentile)),
            str(self.scale_percentile(use_of_force_percentile))
        ])
        return OIG_VISUAL_TOKEN_COLOR_SCHEME[key]\
            if key != '00'\
            else OIG_EXTRA_BLUE_COLOR_SCHEME[str(self.scale_percentile(internal_percentile))]

    def triangle_vertices(self, lengths):
        return [
            (
                self.center['x'] - lengths[0] * math.sin(math.pi/3),
                self.center['y'] - lengths[0] * math.cos(math.pi/3)
            ),
            (
                self.center['x'] + lengths[1] * math.sin(math.pi/3),
                self.center['y'] - lengths[1] * math.cos(math.pi/3)
            ),
            (self.center['x'], self.center['y'] + lengths[2]),
            (
                self.center['x'] - lengths[0] * math.sin(math.pi/3),
                self.center['y'] - lengths[0] * math.cos(math.pi/3)
            )
        ]

    def draw_triangle(self, lengths, fill, stroke, stroke_width=1):
        gizeh.polyline(
            points=self.triangle_vertices(lengths),
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width
        ).draw(self.surface)

    def draw_chart_grid(self, num_of_grid_line, color):
        for i in range(num_of_grid_line):
            self.draw_triangle(
                [(i + 1) * self.spine_length / (num_of_grid_line + 1)] * 3,
                fill=None,
                stroke=color)

    def draw(self, *data):
        chart_color = self.get_visual_token_oig_background(*data)
        soft_black_color = (0.137, 0.121, 0.125)

        gizeh.rectangle(
            xy=(self.center['x'], self.center['y']),
            lx=self.width,
            ly=self.height,
            fill=chart_color
        ).draw(self.surface)
        self.draw_triangle([self.spine_length] * 3, (1, 1, 1, 0.6), None, 0)

        spines = [value * self.spine_length / 100 for value in data]
        self.draw_triangle(
            spines,
            soft_black_color,
            soft_black_color
        )

        self.draw_chart_grid(4, chart_color)

        vertices = self.triangle_vertices(spines)
        for vertex in vertices:
            gizeh.polyline(
                points=[vertex, (self.center['x'], self.center['y'])],
                stroke_width=1,
                stroke=(1, 1, 1)
            ).draw(self.surface)
        for vertex in vertices:
            gizeh.circle(r=4, xy=vertex, fill=(1, 1, 1)).draw(self.surface)
            gizeh.circle(r=3, xy=vertex, fill=soft_black_color).draw(self.surface)

        return self.surface
