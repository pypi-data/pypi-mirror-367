"""fleks.util.console"""

import os


def is_notebook() -> bool:
    """
    Returns true if this runtime is inside a JupyterLab notebook.
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def color_disabled() -> bool:
    """see https://no-color.org/"""
    return True if os.environ.get("NO_COLOR", "") else False
