"""
Module to deploy GUI elements depending on the current environment.

"""

import logging
import os

try:
    import wx
    import wx_ui 
except ImportError:
    logging.info("wx unavailable; using tk_ui")
    wx_ui = False


__all__ = ['ask', 'ask_color', 'ask_dir', 'ask_saveas',
           'copy_file'
           'message', 
           'progress_monitor', 'kill_progress_monitors',
           'test_targetpath',
           ]

_progress_monitors = []


def get_ui():
    if wx_ui and bool(wx.GetApp()):
        return wx_ui
    else:
        import tk_ui
        return tk_ui


def ask_saveas(title = "Save File",
               message = "Please Pick a File Name", 
               ext = [('pickled', "pickled Python object")]):
    return get_ui().ask_saveas(title, message, ext)



def ask_dir(title = "Select Folder",
            message = "Please Pick a Folder",
            must_exist = True):
    return get_ui().ask_dir(title, message, must_exist)



def ask_file(title = "Pick File",
             message = "Please Pick a File", 
             ext = [('*', "all files")],
             directory='',
             mult=False):
    return get_ui().ask_file(title, message, ext, directory, mult)



def ask(title = "Overwrite File?",
        message = "Duplicate filename. Do you want to overwrite?",
        cancel=False,
        default=True, # True=YES, False=NO, None=Nothing
        ):
    return get_ui().ask(title, message, cancel, default)



def ask_color(default=(0,0,0)):
    return get_ui().ask_color(default)


def kill_progress_monitors():
    while len(_progress_monitors) > 0:
        p = _progress_monitors.pop()
        p.terminate()

def show_help(obj):
    return get_ui().show_help(obj)


def message(title, message="", icon='i'):
    return get_ui().message(title, message, icon)


def progress_monitor(i_max=None,
                     title="Task Progress",
                     message="Good luck!",
                     cancel=True):
    """
    With wx-python, show a progress dialog. In Tk this is not fully 
    implemented and merely sends messages to logging.info.
    
    i_max : None | int
        Final state; None: show an indeterminate progress bar.
    title : str
        The window title.
    message : str
        The message; is replaced when :py:meth:`advance` is called with a
        str argument.
    cancel : bool
        Show a cancel button. If the 'cancel' button is clicked, 
        the next call to :py:meth`advance` will raise a KeyboardInterrupt 
        Exception.
    
    """
    dialog = get_ui().progress_monitor(i_max=i_max, title=title, message=message,
                                       cancel=cancel)
    _progress_monitors.append(dialog)
    return dialog


def copy_file(path):
    return get_ui().copy_file(path)


def copy_text(text):
    return get_ui().copy_text(text)



def test_targetpath(path):
    """
    Returns True if path is a valid path to write to, False otherwise. If the
    directory does not exist, the user is asked whether it should be created.
    
    """
    if not path:
        return False
    
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        msg = ("The directory %r does not exist. Should it be created?" % dirname)
        if ask("Create Directory?", msg):
            os.makedirs(dirname)
    
    return os.path.exists(dirname)
