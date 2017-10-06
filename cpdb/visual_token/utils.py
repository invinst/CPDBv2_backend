import os
import shutil


def clear_folder(path):
    try:
        shutil.rmtree(path)
    except OSError:
        pass
    os.makedirs(path)
