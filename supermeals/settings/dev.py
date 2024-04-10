from .base import *

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

SHELL_PLUS = 'ipython'

NOTEBOOK_ARGUMENTS = [
    # exposes IP and port
    "--ip=0.0.0.0",
    "--port=8888",
    # disables the browser
    "--no-browser",
]
