try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings
    warnings.warn("Importing 'pergamon_server_extension' outside a proper installation.")
    __version__ = "dev"
from .handlers import setup_handlers
from .magic import CalliopeMagics
from .help_handler import CalliopeHelpHandler
from .error_hook import load_ipython_extension as load_error_hook
from .error_hook import unload_ipython_extension as unload_error_hook


def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "pergamon_server_extension"
    }]


def _jupyter_server_extension_points():
    return [{
        "module": "pergamon_server_extension"
    }]


def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    setup_handlers(server_app.web_app)
    name = "pergamon_server_extension"
    server_app.log.info(f"Registered {name} server extension")

def load_ipython_extension(ipython):
   try:
       from .completer import register_magic_completer
   except ImportError:
       # Fallback for when module is imported directly
       from pergamon_server_extension.completer import register_magic_completer
   
   ipython.register_magics(CalliopeMagics)
   load_error_hook(ipython)
   
   # Register the completion system
   register_magic_completer(ipython)

def unload_ipython_extension(ipython):
    unload_error_hook(ipython)