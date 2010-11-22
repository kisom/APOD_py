#!/usr/bin/env python
"""
apod.py

written by Kyle Isom <coder@kyleisom.net>

fetches NASA APOD. Usage:
    apod.py [optional directory]

unless specified, the script downloads images to ~/Pictures/apod; the
storage directory may be specified on the command line.
"""

import argparse
import datetime
import os
import re
import sys
import tempfile
import urllib2

########################
# function definitions #
########################

def url_open(url_str):
    """
    Wrapper for urllib2.urlopen that does error handling and
    offers useful debug messages if something explodes.
    """

    try:
        url	= urllib2.urlopen(url_str)

    # something went wrong with the webserver
    except urllib2.HTTPError, e:
        err = sys.stderr.write
        err('APOD download failed with HTTP error ', e.code, '\n')
        sys.exit(2)

    else:
        page 	= url.read()

    return page

def set_background(image_path):
    """
    Attempt to set the desktop image for the system. See the README for 
    supported file types.
    """

    ### here be the dragons of OS-specific hacks!

    platform = sys.platform
    err      = sys.stderr.write

    if "darwin" == platform:
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

    elif "linux2" == platform:
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
            err('couldn\'t find a support desktop environment or window ')
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
            except ImportError:
                err('could not import gconf!\n')
                return False

            except:
                err('ambiguous error setting desktop background!\n')
                return False

            else:
                print 'done!'
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

            
    sys.stderr.write(platform + ' is unsupported.\n')
    return False


############
# URL vars #
############
# base_url: the URL to the APOD page
# image_url: used to store the URL to the large version of the APOD
base_url    = 'http://antwrp.gsfc.nasa.gov/apod/'
image_url   = None

###########
# regexes #
###########
# apod_img: used to pull the large image from the APOD page
# base_img: grabs the base image name, i.e. from image/date/todays_apod.jpg
#           this will return $1 = todays_apod and $2 = jpg - note the 
#           separation of extension from basename.
apod_img    = 'href.+"(image/[\\w+\\./]+\\.[a-z]{3,4})"'
base_img    = '.+/(\\w+)\\.([a-z]{3,4})'

######################
# path and file vars #
######################
# store_dir: where file should be saved
# image_name: the name of the image; taken from the base_img regex in the
#             form $1 + '_date' + $2 where date is in the form yyyymmdd.
# temp: file descriptor for the temporary file the image is download as
#       the file is later moved to store_dir/image_name. Note that this
#       has two elements: temp[0] is the file descriptor, temp[1] is the
#       pathname.
store_dir = os.environ['HOME'] + '/Pictures/apod/'      # default save dir
image_name  = None                                      # image name
temp        = tempfile.mkstemp()                        # temp file

######################
# miscellaneous vars #
######################
today       = '_' + str(datetime.date.today()).replace('-', '')


########################
# begin main code body #
########################

# parse arguments
parser = argparse.ArgumentParser(description='wee little python script'  +
                                 ' to grab NASA\'s APOD')
parser.add_argument('-s', '--set', action = 'store_true', help = 'flag ' +
                    'to cause the script to set the desktop background ' +
                    'to the downloaded image.')
parser.add_argument('-p', '--path', help = 'path to store downloaded '   +
                    'images in')
parser.add_argument('-f', '--force', help='force setting background, '   +
                    'even if image exists already', action = 'store_true')
args = parser.parse_args()

# check to see if both a directory to store files in was specified and
# that the script has write access to that directory.
if hasattr(args, 'path') and args.path:
    if os.access(args.path, os.W_OK):
        store_dir = args.path
        if not store_dir[-1] == '/':
            store_dir += '/'

# ensure we have access to the directory we are trying to store images in
# if not, mkdir()
if not os.access(store_dir, os.F_OK):
    print 'no write permissions on ' + store_dir + '!'
    print 'creating ' + store_dir
    os.mkdir(store_dir)

# fetch page
page    = url_open(base_url + 'astropix.html').split('\n')

# hunt down the APOD
for line in page:
    match 	    = re.search(apod_img, line, re.I)
    if match:
        image_url   = base_url + match.group(1)
        match2      = re.match(base_img, match.group(1), re.I)
        image_name  = match2.group(1) + today + '.' + match2.group(2)
        break

# check to make sure the image URL was actually pulled from the page
if not image_url:
    sys.stderr.write('error retrieving APOD filename!\n')
    sys.exit(3)

# filename to save image as
store_file  = store_dir + image_name

# note the default behaviour is that in the event the file already exists,
# we won't download the image. If the force option is specified, the 
# program will try to set the background.
if os.access(store_file, os.F_OK):
    print 'file already exists!'

    if not args.force:
        sys.exit(4)

elif not os.access(store_file, os.F_OK):
    # save the image to a temporary file
    print 'fetching ' + image_url
    os.write(temp[0], url_open(image_url))

    # need to seek to beginning of file to read out the image to the 
    # actual file.
    os.lseek(temp[0], 0, os.SEEK_SET)


    # diagnostic information
    print 'will store as ' + store_dir + image_name
    
    # save the file
    with open(store_file, 'wb+') as image_f:
        image_f.write(os.read(temp[0]))
    
    print 'download complete!'

    # clean up the temp file
    u_path  = temp[1]
    os.close(temp[0])
    os.unlink(u_path)

# possibly set the background 
if args.set:
    print 'setting desktop background...'
    if not set_background(store_file):
        sys.stderr.write('failed to set desktop background!\n')
    else:
        print 'success!'

# wew survived the gauntlet!
print 'finished!'
