#!/usr/bin/env python

from sys import stderr
err = stderr.write

def main(image_path):
    try:
        from appscript import app, mactypes
        app('Finder').desktop_picture.set(mactypes.File(image_path))
    except ImportError:
        err('could not import appscript. please ensure ')
        err('appscript is installed.\n')
        return False
    except:
        err('error setting wallpaper!')
        return False
    else:
        return True

