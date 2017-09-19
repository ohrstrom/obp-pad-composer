# OBP PAD Composer


`pad-composer` is a rather specific piece of code that likely is not too useful for a larger crowd. (Except for
looking at isolated bits)

It's aim is to fetch metadata about the currently playing track from a radio station using the 
[Open Broadcast Platform](https://www.openbroadcast.org/) [API](https://www.openbroadcast.org/api/v1/?format=json).

The composed metadata then is fed to [ODR-PadEnc](https://github.com/Opendigitalradio/ODR-PadEnc) and sent to the
[Digris](http://digris.ch) DAB+ network via [ODR-DabMod](https://github.com/Opendigitalradio/ODR-DabMod) 
(resp. [ODR-SourceCompanion](https://github.com/Opendigitalradio/ODR-SourceCompanion)).

### Supervisor Example

    [program:pad-composer]
    priority=200
    directory=/home/odr/pad-composer/
    command=/home/odr/pad-composer/env/bin/python composer.py
        --api https://www.openbroadcast.org
        --channel 1
        --timeshift 120
        --dls /home/odr/encoder/meta/dls.txt
        --slides /home/odr/encoder/meta/slides/
    user=odr
    autostart=true
    autorestart=true
    redirect_stderr=True
    stdout_logfile=syslog


