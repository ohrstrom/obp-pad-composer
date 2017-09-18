# OBP PAD Composer


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


