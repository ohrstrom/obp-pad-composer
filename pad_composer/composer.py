# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import requests
import codecs
import shutil
import os


import sched, time

from apscheduler.schedulers.background import BackgroundScheduler

from threading import Thread, Timer

log = logging.getLogger(__name__)

DEFAULT_DLS_PATH = './meta/dls.txt'
DEFAULT_SLIDES_PATH = './meta/slides/'

DEFAULT_SLEEP = 30
DEFAULT_MAX_SLEEP = 30
DEFAULT_API_BASE_URL = 'http://10.40.10.40:8080'
DEFAULT_TIME_SHIFT = 10
DEFAULT_DLS_INTERVAL = 10
DEFAULT_SLIDE_INTERVAL = 45

class PadComposer(object):

    current_dls = []
    current_dls_index = 0

    current_slides = []
    current_slide_index = 0
    last_slide = None


    def __init__(
            self,
            api_base_url,
            channel_id,
            dls_path=DEFAULT_DLS_PATH,
            slides_path=DEFAULT_SLIDES_PATH,
            dl_plus=False,
            timeshift=DEFAULT_TIME_SHIFT,
            dls_interval=DEFAULT_DLS_INTERVAL,
            slide_interval=DEFAULT_SLIDE_INTERVAL
    ):

        self.api_base_url = api_base_url
        self.dls_path = dls_path
        self.slides_path = slides_path
        self.dl_plus = dl_plus
        self.dls_interval = dls_interval
        self.slide_interval = slide_interval

        self.api_url = '{api_base_url}/api/v1/abcast/channel/{channel_id}/on-air/?timeshift={timeshift}&include-dls'.format(
            api_base_url=api_base_url,
            channel_id=channel_id,
            timeshift=timeshift
        )

        # start timers
        self.dls_text_scheduler = BackgroundScheduler()
        self.dls_text_scheduler.add_job(self.set_dls_text, trigger='interval', seconds=dls_interval)
        self.dls_text_scheduler.start()

        self.slide_scheduler = BackgroundScheduler()
        self.slide_scheduler.add_job(self.set_slide, trigger='interval', seconds=slide_interval)
        self.slide_scheduler.start()

        # self.set_dls_text()
        # self.set_slide()


        # clean slide directory
        for file in os.listdir(self.slides_path):
            if file.endswith(".png") or file.endswith(".jpg"):
                path = os.path.join(self.slides_path, file)
                os.unlink(path)

    def run(self):

        while True:

            try:
                start_next = self.get_current_item()
            except (ValueError, requests.ConnectionError) as e:
                log.warning('Unable to connect to API {}'.format(type(e)))
                start_next = None

            if start_next:

                print('got start next: {}'.format(start_next))

                if start_next > DEFAULT_MAX_SLEEP or start_next <= 0:
                    log.debug('start_next is {} seconds - setting to {}'.format(start_next, DEFAULT_MAX_SLEEP))
                    start_next = DEFAULT_MAX_SLEEP
                #log.debug('Got scheduled item - sleeping for {} seconds'.format(start_next))
                time.sleep(int(start_next))

            else:
                #log.debug('No scheduled item - sleeping for {} seconds'.format(DEFAULT_SLEEP))
                time.sleep(DEFAULT_SLEEP)


    def stop(self):
        self.dls_text_scheduler.shutdown()
        self.slide_scheduler.shutdown()


    def get_current_item(self):

        log.info('API request to {}'.format(self.api_url))

        r = requests.get(self.api_url)
        response = r.json()

        dls = response.get('dl_plus' if self.dl_plus else 'dls_text', None)

        if self.current_dls == dls:
            log.debug('DLS unchanged')
        else:
            log.debug('DLS text: {}'.format(' *** '.join(dls)))
            self.current_dls = dls

        slides = response.get('slides', None)

        if self.current_slides == slides:
            log.debug('Slides unchanged')
        else:
            self.current_slides = slides

        return response.get('start_next', None)


    def set_dls_text(self):
        if not self.current_dls:
            log.debug('no current DLS text - retry in 10 seconds...')
            Timer(10, self.set_dls_text).start()
            return

        if len(self.current_dls) < (self.current_dls_index + 1):
            self.current_dls_index = 0

        text = self.current_dls[self.current_dls_index]
        log.debug('setting DLS text to: {}'.format(text))
        with codecs.open(self.dls_path, 'w', "utf-8") as dls_text_file:
            dls_text_file.write(text)

        self.current_dls_index += 1

        #Timer(self.dls_interval, self.set_dls_text).start()



    def set_slide(self):

        if not self.current_slides:
            log.debug('no current slide - retry in 10 seconds...')
            Timer(10, self.set_slide).start()
            return

        if len(self.current_slides) < (self.current_slide_index + 1):
            self.current_slide_index = 0

        slide = self.current_slides[self.current_slide_index]
        log.debug('Setting slide to:\n{:}'.format(slide))

        slide_url = self.api_base_url + slide

        path = os.path.join(self.slides_path, os.path.basename(slide))
        r = requests.get(slide_url, stream=True)

        if self.last_slide and os.path.isfile(self.last_slide):
            os.unlink(self.last_slide)

        # for file in os.listdir(self.slides_path):
        #     if file.endswith(".png") or file.endswith(".jpg"):
        #         path = os.path.join(self.slides_path, file)
        #         os.unlink(path)

        if r.status_code == 200:
            with open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

        self.last_slide = path

        self.current_slide_index += 1


        # calculate duration for transmission
        # assuming 6kbps bandwidth
        slide_size = os.path.getsize(path)
        bwith = 6000

        transmission_time = (slide_size / bwith)

        # add 25% reserve & take into account the pad-encoder 'sleep' of 4 seconds
        next_in = transmission_time * 1.25 + 4
        next_in = self.slide_interval

        # print('slide size:                  {}bytes'.format(slide_size))
        # print('estimated transmission time: {}s'.format(transmission_time))
        # print('next slide in:               {}s'.format(next_in))
        #
        #
        #
        # from random import randint
        # next_in = randint(2, 11)

        log.debug('next slide in: {}'.format(next_in))


        #Timer(next_in, self.set_slide).start()
