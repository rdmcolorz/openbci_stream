import argparse, time, atexit, signal
import os, sys, subprocess, threading, shutil
import pandas as pd
#import pygame
import timeit
from helpers import *
from spectrogram_func import *
from predictModel import *
from predictModel import _parse_function
from osc_helper import *
import asyncio
if sys.version_info.major == 3:
    from pythonosc import dispatcher
    from pythonosc import osc_server
elif sys.version_info.major == 2:
    import OSC

tf.logging.set_verbosity(tf.logging.ERROR)

# globals ########################
g_iter = 0
process_nb = 0
count = 0
sample_data = []
start = 0
file_i = 0

# Path vars #####################
ROOT = os.getcwd()
STREAM_ROOT = os.getcwd() + "/stream_files/"

def stream_window(*args):
    global g_iter
    global sample_data
    global file_i
    
    sample_data.append(args[1:])
    g_iter += 1
    if g_iter == 20:
        sample = np.array(sample_data)
        sample_array = sample.reshape(20,4)
        df = pd.DataFrame(sample_array, columns=["ch1", "ch2", "ch3", "ch4"]) 
        df.to_csv(STREAM_ROOT + "chunk_" + str(file_i), ",")
        print(file_i, "Produced csv") 
        file_i += 1
        g_iter = 0
        sample_data = []


if __name__ == "__main__":
# Collect command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
        default="localhost", 
        help="The ip to listen on")
    parser.add_argument("--port",
        type=int, 
        default=12345, 
        help="The port to listen on")
    parser.add_argument("--address",
        default="/openbci", 
        help="address to listen to")
    parser.add_argument("--option",
        default="print",
        help="Debugger option")
    args = parser.parse_args()

    if sys.version_info.major == 3:
    # Set up necessary parameters from command line
        dispatcher = dispatcher.Dispatcher()
        if args.option=="print":
            dispatcher.map("/openbci", print_message)
            signal.signal(signal.SIGINT, exit_print)

        elif args.option=="record":
            dispatcher.map("/openbci", stream_window)
            signal.signal(signal.SIGINT, exit_print)


        # Display server attributes
        print('--------------------')
        print("-- OSC LISTENER -- ")
        print('--------------------')
        print("IP:", args.ip)
        print("PORT:", args.port)
        print("ADDRESS:", args.address)
        print('--------------------')
        print("%s option selected" % args.option)

        # connect server
        server = osc_server.ThreadingOSCUDPServer(
            (args.ip, args.port), dispatcher)
        server.serve_forever()
    else:
        print("Make sure python is version 3 and up")
    # elif sys.version_info.major == 2:
    #     s = OSC.OSCServer((args.ip, args.port))  # listen on localhost, port 57120
    # if args.option=="print":
    #     s.addMsgHandler(args.address, print_message)
    # elif args.option=="record":
    #     i = 0
    #     while os.path.exists("osc_test%s.txt" % i):
    #         i += 1
    #         filename = "osc_test%i.txt" % i
    #         textfile = open(filename, "w")
    #         textfile.write("time,address,messages\n")
    #         textfile.write("-------------------------\n")
    #         print("Recording to %s" % filename)
    #         signal.signal(signal.SIGINT, close_file)
    # # Display server attributes
    # print('--------------------')
    # print("-- OSC LISTENER -- ")
    # print('--------------------')
    # print("IP:", args.ip)
    # print("PORT:", args.port)
    # print("ADDRESS:", args.address)
    # print('--------------------')
    # print("%s option selected" % args.option)
    # print("Listening...")

    # s.serve_forever()
