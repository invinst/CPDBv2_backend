import os
import shutil


def execute_visual_token_script(driver, path, *args):
    with open(os.path.join(os.path.dirname(__file__), path), 'r') as js_file:
        return driver.execute_script(js_file.read(), *args)


def execute_visual_token_script_async(driver, path, *args):
    with open(os.path.join(os.path.dirname(__file__), path), 'r') as js_file:
        return driver.execute_async_script(js_file.read(), *args)


def clear_folder(path):
    try:
        shutil.rmtree(path)
    except OSError:
        pass
    os.makedirs(path)
