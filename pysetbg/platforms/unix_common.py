#!/usr/bin/env python

import os
from sys import stderr

err = stderr.write

def main(image_path):
    try:
        user     = os.environ['LOGNAME']
    except KeyError:
        return False

    # this is the default X display.
    # in the future, maybe add --display arg?
    os.environ['DISPLAY'] = ':0.0'
    deskenv  = 'ps -au%s -eo command | grep %s | grep -v grep '
    deskenv += '2>&1 > /dev/null' 
    deskenv  = deskenv % (user, '%s')

    desktops = {
        'gnome': { 'process':'gnome-session' },
        'fluxbox': { 'process':'fluxbox' }
    }
    
    for desktop in desktops:
        ret_val = os.system(deskenv % desktops[desktop]['process'])
        if ret_val == 0: break

    else:
        err('couldn\'t find a supported desktop environment or window ')
        err('manager!\n')

        return False    

    # set gconf background string if the user is currently running
    # a GNOME session
    if 'gnome' == desktop:
        try:
            import gconf
            client      = gconf.client_get_default()
            background  = '/desktop/gnome/background/picture_filename'

            if not client.set_string(background, image_path):
                err('failed to set GNOME desktop background!\n')
                return False
            else:
                return True

        except ImportError:
            err('could not import gconf!\n')
            return False

        except:
            err('ambiguous error setting desktop background!\n')
            return False

        else:
            print('done!')
            return True

    # if the user is running fluxbox, look for Esetroot (the first
    # choice) or fbsetbg.
    elif 'fluxbox' == desktop:
        eset_cmd    = 'which Esetroot 2>&1 > /dev/null' 
        fbset_cmd   = 'which fbsetbg 2>&1 > /dev/null'

        ret_val = os.system(eset_cmd)

        if ret_val:
            ret_val = os.system(fbset_cmd)
            if ret_val:
                err('could not find any desktop background-setting ')
                err('programs (tried Esetroot and fbsetbg)!\n')
                return False
            else:
                fbsetbg = '$(which fbsetbg) -f %s' % image_path
                ret_val = os.system(fbsetbg)
                if ret_val:
                    err('error getting fbsetbg to set the background!')
                    return False
                else:
                    return True
        else:
            esetroot = '$(which Esetroot) -scale %s' % image_path
            ret_val = os.system(esetroot)
            
            if ret_val:
                err('error getting Esetroot to set the background!')
                return False
            else:
                return True

