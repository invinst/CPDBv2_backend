import multiprocessing
import subprocess
import os
import tempfile

from tqdm import tqdm


def make_frame(draw_func, data, frame_count, ind, width, height):
    frame = draw_func(data, frame_count, ind, width, height)
    f, path = tempfile.mkstemp('.png')
    os.close(f)
    frame.write_to_png(path)
    return path


class FFMpegWriter(object):
    bin_path = '/usr/bin/ffmpeg'
    outfile = '/CPDB/CPDBv2_backend/out.mp4'

    def __init__(self, width, height, frame_rate=40):
        self.frame_rate = frame_rate
        self.width = width
        self.height = height

    def run(self, draw_func, data, frame_count, out_path):
        command = [
            self.bin_path,
            '-y',
            '-f', 'image2pipe',
            '-r', str(self.frame_rate),
            '-vcodec', 'png',
            '-r', str(self.frame_rate),
            '-i', '-',
            '-vcodec', 'libx264',
            '-r', str(self.frame_rate),
            '-pix_fmt', 'yuv420p',
            '-loglevel', 'quiet',
            out_path]

        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        frames = [
            pool.apply_async(make_frame, (draw_func, data, frame_count, ind, self.width, self.height))
            for ind in range(frame_count)]

        proc = subprocess.Popen(
            command, stdin=subprocess.PIPE,
            stdout=None, stderr=subprocess.STDOUT)

        for frame in tqdm(frames):
            png_path = frame.get()
            with open(png_path, 'rb') as f:
                proc.stdin.write(f.read())
                proc.stdin.flush()
            os.remove(png_path)
        proc.stdin.close()
        proc.wait()
