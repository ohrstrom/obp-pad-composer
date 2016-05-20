#!/usr/bin/env python
from __future__ import unicode_literals

import argparse
import os
import logging
import codecs
import shutil
import sys
import time
import sched
from threading import Timer
import requests
from logging.config import fileConfig

NUM_CHARS = 72
DEFAULT_SLEEP = 10

DEFAULT_API_BASE_URL = 'http://10.40.10.40:8080'
DEFAULT_CHANNEL_ID = 1
DEFAULT_TIME_SHIFT = 10
DEFAULT_DLS_INTERVAL = 10

fileConfig('logging.ini')
log = logging.getLogger()


class Composer:

    def __init__(self, api_base_url, channel_id, timeshift, dls_interval, dls_path, slides_path):


        log.info('{:}: {:}'.format('api_base_url', api_base_url))
        log.info('{:}: {:}'.format('channel_id', channel_id))
        log.info('{:}: {:}'.format('timeshift', timeshift))
        log.info('{:}: {:}'.format('dls_path', dls_path))
        log.info('{:}: {:}'.format('slides_path', slides_path))
        log.info('{:}: {:}'.format('slides_path', slides_path))
        log.info('{:}: {:}'.format('dls_interval', dls_interval))


        config_errors = False

        if os.path.isfile(dls_path):
            log.info('{:} - file exists'.format(dls_path))
        else:
            log.error('{:} - file does not exist!'.format(dls_path))
            sys.exit(1)

        if os.access(dls_path, os.W_OK):
            log.info('{:} - file is writable'.format(dls_path))
        else:
            log.error('{:} - file not writable!'.format(dls_path))
            sys.exit(1)


        if os.path.isdir(slides_path):
            log.info('{:} - directory exists'.format(slides_path))
        else:
            log.error('{:} - directory does not exist!'.format(slides_path))
            sys.exit(1)

        if os.access(slides_path, os.W_OK):
            log.info('{:} - directory is writable'.format(slides_path))
        else:
            log.error('{:} - directory not writable!'.format(slides_path))
            sys.exit(1)

        self.api_url = '{0}/api/v1/abcast/channel/{1}/on-air/?timeshift={2}&include-dls'.format(
            api_base_url,
            channel_id,
            timeshift
        )

        self.api_base_url = api_base_url
        self.dls_path = dls_path
        self.slides_path = slides_path

        self.current_dls = None
        self.current_dls_index = 0
        self.set_dls_text(dls_interval)

        self.current_slides = None

    def update_current_item(self):

        log.debug('Calling API at: {:}'.format(self.api_url))

        r = requests.get(self.api_url)
        response = r.json()

        dls = response.get('dls_text', None)

        if dls and len(dls) > 0:
            self.current_dls = dls
            for text in dls:
                print text

        else:
            text = None

        # if not self.current_dls == text:
        #     self.current_dls = text
        #     self.set_dls_text(text)
        # else:
        #     log.debug('Text unchanged')


        slides = response.get('slides', None)

        if not self.current_slides == slides:
            self.current_slides = slides
            self.set_slides(slides)
        else:
            log.debug('Slide unchanged')


        return response.get('start_next', None)


    def set_dls_text(self, interval):
        Timer(interval, self.set_dls_text, {interval}).start()
        if not self.current_dls:
            return

        if len(self.current_dls) < (self.current_dls_index + 1):
            self.current_dls_index = 0

        text = self.current_dls[self.current_dls_index]
        log.debug('Setting dls text to:\n{:}'.format(text))
        with codecs.open(self.dls_path, 'w', "utf-8") as dls_text_file:
            dls_text_file.write(text)

        self.current_dls_index += 1

    def __orig__set_dls_text(self, text):

        print 'set_dls_text: {}'.format(text)

        log.debug('Setting dls text to:\n{:}'.format(text))

        with codecs.open(self.dls_path, 'w', "utf-8") as dls_text_file:
            dls_text_file.write(text)


    def set_slides(self, slides):

        for file in os.listdir(self.slides_path):
            if file.endswith(".png"):
                path = os.path.join(self.slides_path, file)
                os.unlink(path)


        for slide in slides:

            slide_url = self.api_base_url + slide
            log.debug('Setting dls slide to: {:}'.format(slide_url))

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
            type=int,
            metavar='',
            help='Time-shift [{0}]'.format(DEFAULT_TIME_SHIFT),
            default=DEFAULT_TIME_SHIFT
    )
    parser.add_argument(
            '--dls_interval',
            type=int,
            metavar='',
            help='Interval for DLS text update [{0}]'.format(DEFAULT_TIME_SHIFT),
            default=DEFAULT_DLS_INTERVAL
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
            log.warning('Unable to connect to API - {:} {:}'.format(type(e), e.args))
            start_next = None

        if start_next:
            if start_next > 60:
                start_next = 60
            log.debug('Got scheduled item - sleeping for {:} seconds'.format(start_next))
            time.sleep(start_next)

        else:
            log.debug('No scheduled item - sleeping for {:} seconds'.format(DEFAULT_SLEEP))
            time.sleep(DEFAULT_SLEEP)









