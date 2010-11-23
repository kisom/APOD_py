#!/usr/bin/env python
"""
module to set the background in python.

core written by Kyle Isom <coder@kyleisom.net>
platforms:
    darwin: Kyle Isom <coder@kyleisom.net>
    unix_common: Kyle Isom <coder@kyleisom.net>
    win32: trafficone <trafficone@devio.us>

platforms should implement main(image_path) as a boolean method that should
set or call the background-setting code.
"""

import sys

unix_common = [ 'linux', 'openbsd', 'freebsd', 'netbsd' ]
supported   = [ 'darwin', 'unix_common' ]


def set_bg(image_path):
    """
    Attempt to set the desktop image for the system. See the README for 
    supported file types.
    """

    # get the platform and set up a shortcut variable to stderr.write()
    platform = sys.platform
    err      = sys.stderr.write

    # a number of UNIX platforms will be handled similarly
    for system in unix_common:
        if system == platform[:-1]:
            platform = 'unix_common'

    # supported platforms should be added to the supported list
    if platform in supported:
        try:
            # platform magic
            platform_import = 'from platforms import %s as set_bg'
            platform_import = platform_import % platform
            exec platform_import

        # platform not supported, even though it should be
        except ImportError:
            err('this platform should be supported but isn\'t ')
            err('- could not import your platform-specific code!')
            err('\n\tThis needs to be brought to the attention of')
            err(' the devs.\n')
            return False
            
        else:
            return set_bg.main(image_path)
            
    else:
        err(platform + ' is unsupported.\n')
        return False


