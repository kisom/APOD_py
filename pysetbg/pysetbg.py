#!/usr/bin/env python

import sys

unix_common = [ 'linux2', 'openbsd4' ]
supported   = [ 'darwin', 'unix_common' ]


def set_background(image_path):
    """
    Attempt to set the desktop image for the system. See the README for 
    supported file types.
    """

    ### here be the dragons of OS-specific hacks!
    platform = sys.platform
    err      = sys.stderr.write

    if platform in unix_common:
        platform = 'unix_common'

    if platform in supported:
        try:
            platform_import = 'from platforms import %s as set_bg'
            platform_import = platform_import % platform
            exec platform_import

        except ImportError:
            err('unsupported platform - could not import!')
            return False
            
        else:
            return set_bg.main(image_path)
            
    else:
        sys.stderr.write(platform + ' is unsupported.\n')
        return False


