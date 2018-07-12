import cairo


def draw_frame(frame_num, width, height):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # Fill background
    ctx.rectangle(0, 0, width, height)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()

    # Draw content
    offset = frame_num * 2
    l = width / 8
    r = 7 * width / 8
    t = height / 8
    b = 7 * height / 8

    ctx.move_to(l + offset, t)
    ctx.line_to(r - offset, b)
    ctx.move_to(l, t + offset)
    ctx.line_to(r, b - offset)
    ctx.move_to(r - offset, t)
    ctx.line_to(l + offset, b)
    ctx.move_to(l, b - offset)
    ctx.line_to(r, t + offset)

    ctx.set_source_rgb(0.5, 0, 1)
    ctx.set_line_width(height / 64)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()

    return surface
