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
from pysetbg.pysetbg import set_bg

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

def log_message(log_string):
	"""
	Prepend a timestamp onto the progress and error messages if the
	command line argument is set. Makes for a pretty log file.
	"""
	if args.timestamp:
		log_time    = datetime.datetime.strftime(datetime.datetime.now(), \
		              "%Y-%m-%d %H:%M:%S")
		log_time    = '[' + log_time + ']'
		return log_time + " " + log_string
	else:
		return log_string


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
# today: the date in a string format appropriate for appending to the 
#        image filename.
# image_size: number of bytes written
today       = '_' + str(datetime.date.today()).replace('-', '')
image_size  = 0


########################
# begin main code body #
########################

# parse arguments
parser = argparse.ArgumentParser(description='wee little python script'  +
                                 ' to grab NASA\'s APOD')
parser.add_argument('-f', '--force', help='force setting background, '   +
                    'even if image exists already', action = 'store_true')
parser.add_argument('-o', '--overwrite', help='overwrite existing image',
                    action='store_true')
parser.add_argument('-p', '--path', help = 'path to store downloaded '   +
                    'images in')
parser.add_argument('-s', '--set', action = 'store_true', help = 'flag ' +
                    'to cause the script to set the desktop background ' +
                    'to the downloaded image.')
parser.add_argument('-t', '--timestamp', action = 'store_true',
                    help = 'flag to cause timestamps to be prepended to' +
                    ' progress and error messages.')
args = parser.parse_args()


# check to see if both a directory to store files in was specified and
# that the script has write access to that directory.
if args.path:
    store_dir = args.path
    if not store_dir[-1] == '/':
        store_dir += '/'

# ensure we have access to the directory we are trying to store images in
# if not, mkdir()
if not os.access(store_dir, os.W_OK):
    print log_message('no write permissions on ' + store_dir + '!')
    print log_message('creating ' + store_dir)
    try:
        os.makedirs(store_dir)
    except OSError:
        sys.stderr.write('could not create dir ' + store_dir + '!\n')
        sys.exit(2)

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
if os.access(store_file, os.F_OK) and not args.overwrite:
    print log_message('file already exists!')

    if not args.force:
        sys.exit(4)

elif not os.access(store_file, os.F_OK) or args.overwrite:
    if os.access(store_file, os.F_OK): print log_message('file exists...')
    if args.overwrite: print log_message('will overwrite!')
    # save the image to a temporary file
    print log_message('fetching ' + image_url)
    image_size = os.write(temp[0], url_open(image_url))

    # need to seek to beginning of file to read out the image to the 
    # actual file.
    os.lseek(temp[0], 0, os.SEEK_SET)


    # diagnostic information
    print log_message('will store as ' + store_file)
    
    # save the file
    with open(store_file, 'wb+') as image_f:
        image_f.write(os.read(temp[0], image_size))
    
    print log_message('file saved to ' + store_file)
    print log_message('download complete!')

    # clean up the temp file
    u_path  = temp[1]
    os.close(temp[0])
    os.unlink(u_path)

# possibly set the background 
if args.set:
    print log_message('setting desktop background...')
    if not set_bg(store_file):
        sys.stderr.write('failed to set desktop background!\n')
    else:
        print log_message('success!')

# wew survived the gauntlet!
print log_message('finished!')
