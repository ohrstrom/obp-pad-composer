#!/usr/bin/env python
from __future__ import unicode_literals

import argparse
import os
import shutil
import sys
import time
import requests
from termcolor import cprint

NUM_CHARS = 72
DEFAULT_SLEEP = 10

DEFAULT_API_BASE_URL = 'http://10.40.10.40:8080'
DEFAULT_CHANNEL_ID = 1
DEFAULT_TIME_SHIFT = 10

class Composer:

    def __init__(self, api_base_url, channel_id, timeshift, dls_path, slides_path):

        cprint('#' * NUM_CHARS, 'green')
        cprint('{:14s}: {:}'.format('api_base_url', api_base_url), 'green')
        cprint('{:14s}: {:}'.format('channel_id', channel_id), 'green')
        cprint('{:14s}: {:}'.format('timeshift', timeshift), 'green')
        cprint('{:14s}: {:}'.format('dls_path', dls_path), 'green')
        cprint('{:14s}: {:}'.format('slides_path', slides_path), 'green')
        print

        config_errors = False

        if os.path.isfile(dls_path):
            cprint('{:14s}: {:} - file exists'.format('OK', dls_path), 'green')
        else:
            cprint('{:14s}: {:} - file does not exist!'.format('ERROR', dls_path), 'red')
            sys.exit(1)

        if os.access(dls_path, os.W_OK):
            cprint('{:14s}: {:} - file is writable'.format('OK', dls_path), 'green')
        else:
            cprint('{:14s}: {:} - file not writable!'.format('ERROR', dls_path), 'red')
            sys.exit(1)


        if os.path.isdir(slides_path):
            cprint('{:14s}: {:} - directory exists'.format('OK', slides_path), 'green')
        else:
            cprint('{:14s}: {:} - directory does not exist!'.format('ERROR', slides_path), 'red')
            sys.exit(1)

        if os.access(slides_path, os.W_OK):
            cprint('{:14s}: {:} - directory is writable'.format('OK', slides_path), 'green')
        else:
            cprint('{:14s}: {:} - directory not writable!'.format('ERROR', slides_path), 'red')
            sys.exit(1)

        self.api_url = '{0}/api/v1/abcast/channel/{1}/on-air/?timeshift={2}&include-dls'.format(
            api_base_url,
            channel_id,
            timeshift
        )

        self.api_base_url = api_base_url
        self.dls_path = dls_path
        self.slides_path = slides_path

        self.current_dls_text = None
        self.current_dls_slide = None


    def update_current_item(self):

        r = requests.get(self.api_url)
        response = r.json()

        dls_text = response.get('dls_text', None)

        if dls_text and len(dls_text) > 0:
            text = dls_text[0]
        else:
            text = None

        if not self.current_dls_text == text:
            self.current_dls_text = text
            self.set_dls_text(text)
        else:
            cprint('Text unchanged', 'yellow')


        dls_slides = response.get('dls_slides', None)

        if dls_slides and len(dls_slides) > 0:
            slide = dls_slides[0]
        else:
            slide = None

        if not self.current_dls_slide == slide:
            self.current_dls_slide = slide
            self.set_dls_slide(slide)
        else:
            cprint('Slide unchanged', 'yellow')


        return response.get('start_next', None)


    def set_dls_text(self, text):

        cprint('Setting dls text to:\n{:}'.format(text), 'cyan')

        with open(self.dls_path, 'w') as dls_text_file:
            dls_text_file.write(text)


    def set_dls_slide(self, slide):

        slide_url = self.api_base_url + slide
        cprint('Setting dls slide to: {:}'.format(slide_url), 'cyan')

        for file in os.listdir(self.slides_path):
            if file.endswith(".png"):
                path = os.path.join(self.slides_path, file)
                os.unlink(path)


        path = os.path.join(self.slides_path, os.path.basename(slide))
        r = requests.get(slide_url, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)






if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-a', '--api',
            dest='api_base_url',
            metavar='',
            help='API endpoint [{0}]'.format(DEFAULT_API_BASE_URL),
            default=DEFAULT_API_BASE_URL
    )
    parser.add_argument(
            '-c', '--channel',
            dest='channel_id',
            metavar='',
            help='Channel ID [{0}]'.format(DEFAULT_CHANNEL_ID),
            default=DEFAULT_CHANNEL_ID
    )
    parser.add_argument(
            '-t', '--timeshift',
            metavar='',
            help='Time-shift [{0}]'.format(DEFAULT_TIME_SHIFT),
            default=DEFAULT_TIME_SHIFT
    )
    parser.add_argument(
            '-d', '--dls',
            dest='dls_path',
            metavar='PATH',
            help='Full path to dls text file',
            required=True
    )
    parser.add_argument(
            '-s', '--slides',
            dest='slides_path',
            metavar='PATH',
            help='Full path to slides directory',
            required=True
    )
    args = parser.parse_args()


    composer = Composer(**args.__dict__)

    while True:


        try:
            start_next = composer.update_current_item()
        except (ValueError, requests.ConnectionError) as e:
            cprint('{:14s}: Unable to connect to API - {:} {:}'.format('WARNING', type(e), e.args), 'yellow')
            start_next = None

        if start_next:
            if start_next > 60:
                start_next = 60
            cprint('{:14s}: Got scheduled item - sleeping for {:} seconds'.format('OK', start_next), 'green')
            time.sleep(start_next)

        else:
            cprint('{:14s}: No scheduled item - sleeping for {:} seconds'.format('OK', DEFAULT_SLEEP), 'cyan')
            time.sleep(DEFAULT_SLEEP)









