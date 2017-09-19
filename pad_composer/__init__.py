# -*- coding: utf-8 -*-
import logging
import sys

import click
import click_log

from .composer import (
    PadComposer,
    DEFAULT_API_BASE_URL, DEFAULT_TIME_SHIFT, DEFAULT_DLS_INTERVAL, DEFAULT_SLIDE_INTERVAL
)

__version__ = '0.0.1'

log = logging.getLogger(__name__)
click_log.basic_config(log)


@click.group()
def cli():
    pass


@cli.command()
@click_log.simple_verbosity_option(log)
@click.option('--api', '-a', 'api_base_url', type=str, required=True, default=DEFAULT_API_BASE_URL,
              help='API endpoint [{0}]'.format(DEFAULT_API_BASE_URL)
              )
@click.option('--channel', '-c', 'channel_id', type=int, default=1,
              help='Channel ID [1]'
              )
@click.option('--dls', '-d', 'dls_path', type=click.Path(), required=True,
              help='Path to DLS text file'
              )
@click.option('--slides', '-s', 'slides_path', type=click.Path(), required=True,
              help='Path to slides directory'
              )
@click.option('--dl-plus', '-p', 'dl_plus', is_flag=True, default=False,
              help='Include DL+ notation in dls text [false]'
              )
# timing related
@click.option('--timeshift', '-t', type=int, default=DEFAULT_TIME_SHIFT,
              help='Time-shift [{0}]'.format(DEFAULT_TIME_SHIFT)
              )
@click.option('--dls-interval', 'dls_interval', type=int, default=DEFAULT_DLS_INTERVAL,
              help='Interval for DLS text update [{0}]'.format(DEFAULT_DLS_INTERVAL)
              )
@click.option('--slide-interval', 'slide_interval', type=int, default=DEFAULT_SLIDE_INTERVAL,
              help='Interval for slide update [{0}]'.format(DEFAULT_SLIDE_INTERVAL)
              )

def run(**kwargs):

    while True:

        c = PadComposer(**kwargs)
        try:
            c.run()
        except KeyboardInterrupt:
            log.info('Ctrl-c received! Stop composer')
            c.stop()
            sys.exit()
