#!/usr/bin/env python3

# for access to the GPIO on the RasPi
import RPi.GPIO as gpio


import sys
import time
import threading

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

RED = 0
ORANGE = 1
BLUE = 2

INTERVAL=2

lOn=['R','O','G']
lOff=['r','o','g']

colorName=['RED','ORANGE','BLUE']
lightLevels=[0,0,0]
ioPins=[23,24,25]

def lightController(color):
    ''' Worker thread that will handle the blinking of a light.'''

    # make our pin an output
    gpio.setup(ioPins[color],gpio.OUT)

    while lightLevels[color]!=-1:
        next=time.time()+INTERVAL
        level=lightLevels[color]

        if level==0:
            gpio.output(ioPins[color],False)
        else:
            gpio.output(ioPins[color],True)
            if level<100:
                time.sleep(INTERVAL*level/100.0)
                gpio.output(ioPins[color],False)
        now=time.time()
        if now<next:
            time.sleep(next-now)

    gpio.output(ioPins[color],False)
    print("Done %s!" % colorName[color])


def rpcServer():
    # restrict to a particular path
    class RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths=('/RPC2',)

    # create RPC server
    server=SimpleXMLRPCServer(("0.0.0.0", 8000),requestHandler=RequestHandler,allow_none=True)
    server.register_introspection_functions()

    # register functions for pole lights
    server.register_function(red)
    server.register_function(orange)
    server.register_function(blue)

    # method to stop controller
    server.register_function(stop)

    # run the server's main loop
    while lightLevels[RED]!=-1:
        server.handle_request()

    print('Done server!')

def light(color,level):
    if level<0:
        level=0
    elif level>100:
        level=100
    lightLevels[color]=level
    print("%s %s%% on" % (colorName[color],level))
    return level

def red(level):
    ''' Control the red light 0=off 100=permanent on.'''
    return light(RED,level)

def orange(level):
    ''' Control the orange light 0=off 100=permanent on.'''
    return light(ORANGE,level)

def blue(level):
    ''' Control the blue light 0=off 100=permanent on.'''
    return light(BLUE,level)

def stop():
    ''' Switch off all the lights and stop the program.'''
    # signal light threads to end
    lightLevels[RED]=-1
    lightLevels[ORANGE]=-1
    lightLevels[BLUE]=-1


# initialize the GPIO
gpio.cleanup()
gpio.setmode(gpio.BCM)

redThread=threading.Thread(target=lightController,args=(RED,))
redThread.start()
blueThread=threading.Thread(target=lightController,args=(BLUE,))
blueThread.start()
orangeThread=threading.Thread(target=lightController,args=(ORANGE,))
orangeThread.start()

rpcServerThread=threading.Thread(target=rpcServer)
rpcServerThread.start()

redThread.join()
orangeThread.join()
blueThread.join()

gpio.cleanup()

print('Waiting for end of server thread...')

rpcServerThread.join()

print('All done!!')
