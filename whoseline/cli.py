import os
import subprocess
import sys


def launch_app():
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    subprocess.run(['solara', 'run', app_path, '--production'] + sys.argv[1:])
