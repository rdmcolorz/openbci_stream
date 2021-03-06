import argparse
import time
import os
import sys

import pandas as pd
import numpy as np
import signal
if sys.version_info.major == 3:
    from pythonosc import dispatcher
    from pythonosc import osc_server
elif sys.version_info.major == 2:
    import OSC

from osc_helper import print_message, exit_print
from colored import fg, attr

#tf.logging.set_verbosity(tf.logging.ERROR)

# globals ########################
ITER = 0
FILE_ITER = 0
CHANNELS = ['ch1', 'ch2', 'ch3', 'ch4']
CH_DATA = {ch: [] for ch in CHANNELS}
NB_CHANNELS = len(CH_DATA.keys())
INTERVAL = 2 # seconds to record of each label
 
# Path vars #####################
STREAM_ROOT = os.getcwd() + "/stream_files/"

# trying to make stream_window faster so we don't get duplicate data, 
# but wonder if it is the problem at all though.
# needs testing.

def record_to_file(*args):
    textfile.write(str(time.time()) + ",")
    textfile.write(",".join(str(x) for x in args))
    textfile.write("\n")

# Save recording, clean exit from record mode
def close_file(*args):
    print("\nFILE SAVED")
    textfile.close()
    sys.exit(0)

def output_command(s_label, color):
    """function to color labels and output to terminal"""
    color = fg(color)
    reset = attr('reset')
    print(
        color
        + "#" * 42 + "\n" 
        + "#" * 42 + "\n" 
        + "    {} \n".format(s_label)
        + "#" * 42 + "\n" 
        + "#" * 42 
        + reset
        )

def stream_window(*args):
    global ITER, FILE_ITER
    global CH_DATA

    if ITER == 0 and FILE_ITER % 2 == 0:
        print(colored(
                    "#" * 21 + "\n" 
                    + "#" * 21 + "\n"
                    + "    Say command : \n"
                    + "#" * 21 + "\n"
                    + "#" * 21, 'yellow'
                    ))

    for x in range(1, NB_CHANNELS + 1):
        CH_DATA['ch{}'.format(x)].append(round(args[x], 2))

    g_iter += 1
    if FILE_ITER == 10: # the number of files until it overwrites the first one.
        FILE_ITER = 0
    if g_iter == 200 * INTERVAL: 
        # number of lines of data until packing into a txt file.
        df = pd.DataFrame(CH_DATA)
        if FILE_ITER % 2 == 0:
            df.to_csv(STREAM_ROOT + str(FILE_ITER) + ".txt", ",")
            print("Produced csv no: {}".format(FILE_ITER))
        FILE_ITER += 1
        g_iter = 0
        CH_DATA = {ch: [] for ch in CHANNELS}

if __name__ == "__main__":
# Collect command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="localhost", 
                        help="The ip to listen on"
                        )
    parser.add_argument("--port",
                        type=int, 
                        default=12345, 
                        help="The port to listen on"
                        )
    parser.add_argument("--address",
                        default="/openbci", 
                        help="address to listen to"
                        )
    parser.add_argument("--option",
                        default="print",
                        help="Debugger option"
                        )
    args = parser.parse_args()

    if sys.version_info.major == 3:
    # Set up necessary parameters from command line
        dispatcher = dispatcher.Dispatcher()
        
        if args.option=="print":
            dispatcher.map("/openbci", print_message)
            signal.signal(signal.SIGINT, exit_print)

        elif args.option=="record":
            i = 0
            while os.path.exists("osc_record/osc_test%s.txt" % i):
                i += 1
            filename = "osc_record/osc_test%i.txt" % i
            textfile = open(filename, "w")
            textfile.write("time,address,ch1,ch2,ch3,ch4\n")
            print("Recording to %s" % filename)
            dispatcher.map("/openbci", record_to_file)
            signal.signal(signal.SIGINT, close_file)
        
        elif args.option=="predict":
            dispatcher.map("/openbci", stream_window)
            signal.signal(signal.SIGINT, exit_print)

        # Display server attributes
        print('--------------------')
        print(" -- OSC LISTENER -- ")
        print('--------------------')
        print("IP:", args.ip)
        print("PORT:", args.port)
        print("ADDRESS:", args.address)
        print('--------------------')
        print("%s option selected" % args.option)

        # connect server
        server = osc_server.BlockingOSCUDPServer(
            (args.ip, args.port), dispatcher)
        server.serve_forever()
    else:
        print("Make sure python is version 3 and up")