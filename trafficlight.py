#!/usr/bin/env python3

# for access to the GPIO on the RasPi
import RPi.GPIO as gpio

import sys
import time
import threading

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

INTERVAL=2

keepGoing=True
lightLevels={}

def lightController(color,ioPin):
    """ Worker thread that will handle the blinking of a light."""

    # make our pin an output
    gpio.setup(ioPin,gpio.OUT)

    lightLevels[color]=0

    while keepGoing==True:
        next=time.time()+INTERVAL
        level=lightLevels[color]

        if level==0:
            gpio.output(ioPin,False)
        else:
            gpio.output(ioPin,True)
            if level<100:
                time.sleep(INTERVAL*level/100.0)
                gpio.output(ioPin,False)
        now=time.time()
        if now<next:
            time.sleep(next-now)

    gpio.output(ioPin,False)
    print(f"Done {color}!")


def rpcServer():
    # restrict to a particular path
    class RequestHandler(SimpleXMLRPCRequestHandler):
    	rpc_paths=("/RPC2",)

    # create RPC server
    with SimpleXMLRPCServer(("0.0.0.0", 8000),requestHandler=RequestHandler,allow_none=True) as server:
        server.register_introspection_functions()

        # register functions for pole lights
        server.register_function(red)
        server.register_function(orange)
        server.register_function(blue)

        # method to stop controller
        server.register_function(stop)

	    # run the server's main loop
        while keepGoing==True:
            server.handle_request()

    print("Done server!")

def light(color,level):
    if level<0:
        level=0
    elif level>100:
        level=100
    lightLevels[color]=level
    print(f"{color} {level}% on")
    return level

def red(level):
    """ Control the red light 0=off 100=permanent on."""
    return light("red",level)

def orange(level):
    """ Control the orange light 0=off 100=permanent on."""
    return light("orange",level)

def blue(level):
    """ Control the blue light 0=off 100=permanent on."""
    return light("blue",level)

def stop():
    """ Switch off all the lights and stop the program."""
    global keepGoing
    # signal light threads to end
    keepGoing=False


# initialize the GPIO
gpio.setmode(gpio.BCM)

print("Starting threads")

redThread=threading.Thread(target=lightController,args=("red",23))
redThread.start()
blueThread=threading.Thread(target=lightController,args=("blue",25))
blueThread.start()
orangeThread=threading.Thread(target=lightController,args=("orange",24))
orangeThread.start()

rpcServerThread=threading.Thread(target=rpcServer)
rpcServerThread.start()

redThread.join()
orangeThread.join()
blueThread.join()

gpio.cleanup()

print("Waiting for end of server thread...")

rpcServerThread.join()

print("All done!")
