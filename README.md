# ODR Stream Router

[![Build Status](https://travis-ci.org/digris/odr-stream-router.svg?branch=master)](https://travis-ci.org/digris/odr-stream-router)

A fairly primitive tool to route ODR zmq streams.

The aim of `odroute` is to achieve two goals:

 - Providing ways to handle a fallback for DAB+ streams generated with `odr-dabmod`.
   E.g. in the situation when running a dedicated encoder box in the studio, but in case of connection- or
   encoder-failure an automatic failover to a central encoder instance (encoding a webstream) is desired.
 - Providing way to distribute DAB+ streams through a single connection from an encoder to multiple MUXes.


## Installation


### Via PyPi

    pip install odroute

    
### From GitHub

    pip install -e git+https://github.com/digris/odr-stream-router.git#egg=odroute

    
### From Source

    git clone https://github.com/digris/odr-stream-router.git
    cd odr-stream-router
    pip install -e .


## Usage

    odroute run --help

#### Simple Example

Listen on ports *5001* and *5002* and output the active port to *tcp://localhost:9001* - switching
inputs after 0.5 seconds of 'inactivity/activity'.

`-s/--source` and `-o/--output` can both be specified multiple times.

The priority of the input ports is specified through the order. So in this example port *5001* is forwarded if
available, else packages from the socket on *5002* are used.

    odroute run -s 5001 -s 5002 -o tcp://localhost:9001 -d 0.5 -v debug

#### Telnet Interface

Version `0.0.2` provides a telnet interface that can list the configured inputs and outputs and the currently
*active* input.  
Further it provides functionality fo *force* an input to be used (instead of relying on the fallback 
behaviour).


use option `--telnet` resp. `-t` with either *port* to listen on or in *ip:port* to bind.  
See `odroute run --help`

    odroute run -s 5001 -s 5002 -o tcp://localhost:9001 -t 127.0.0.1:4001
    
Connect with telnet and run `help` to see the available commands

    telnet 127.0.0.1 4001
    
Or use `netcat`:

    echo help             | nc 127.0.0.1 4001
    echo input.list       | nc 127.0.0.1 4001
    echo input.force 5002 | nc 127.0.0.1 4001
    echo input.current    | nc 127.0.0.1 4001

