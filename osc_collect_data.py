import argparse, time, os, sys
import pandas as pd
import numpy as np
from osc_helper import *
import signal
from colored import fg, attr
if sys.version_info.major == 3:
    from pythonosc import dispatcher
    from pythonosc import osc_server
elif sys.version_info.major == 2:
    import OSC

#tf.logging.set_verbosity(tf.logging.ERROR)

# globals ########################
g_iter = 0
file_iter = 0
label_iter = 0
sample_data = []

# CH_NAME = list(CH_DATA.keys())

CHANNELS = ['ch1', 'ch2', 'ch3', 'ch4']
CH_DATA = {ch: [] for ch in CHANNELS}
NB_CHANNELS = len(CH_DATA.keys())

LABELS = ['zero', 'one', 'two', 'three', 'four', 
            'five', 'six', 'seven', 'eight', 'nine',
            'left', 'right', 'stop', 'go', 'up', 
            'down']
LABEL_COUNT = {label:0 for label in LABELS}
NB_LABELS = len(LABELS)

COLORS = ['red', 'green', 'yellow', 'light_blue', 'magenta', 
            'cyan', 'white', 'light_gray', 'light_red', 'light_green',
            'light_yellow', 'cyan_3', 'green_3b', 'blue_violet', 'orange', 
            'yellow']
INTERVAL = 1.5 # seconds to record of each label
 
# Path vars #####################
ROOT = os.getcwd()

# trying to make stream_window faster so we don't get duplicate data, 
# but wonder if it is the problem at all though.
# needs testing.

# Save recording, clean exit from record mode
# def close_file(*args):
#     print("\nFILE SAVED")
#     textfile.close()
#     sys.exit(0)

def output_command(s_label, color):
    color = fg(color)
    reset = attr('reset')
    print(color + 
            "#" * 42 + "\n" + 
            "#" * 42 + "\n" + 
            "    {} \n".format(s_label) +
            "#" * 42 + "\n" +
            "#" * 42 +
            reset)

def dframe2csv(csv_path):
    global LABEL_COUNT
    global label_iter
    
    df = pd.DataFrame(CH_DATA)
    label = LABELS[label_iter]
    df.to_csv(csv_path + "/{}/".format(label) + str(LABEL_COUNT[label]) + ".txt", ",")
    print("Produced csv no: {} lable: {}".format(file_iter, label))
    LABEL_COUNT[label] += 1 
    if label_iter == NB_LABELS - 1:
        label_iter = 0
    else:
        label_iter += 1
  

def stream_window(*args):
    global g_iter, file_iter, label_iter
    global CH_DATA

    if g_iter == 0:
        output_command(LABELS[label_iter], COLORS[label_iter])

    for x in range(1, NB_CHANNELS + 1):
        CH_DATA['ch{}'.format(x)].append(round(args[x + 1], 2))

    g_iter += 1
    if g_iter == 200 * INTERVAL: # number of lines of data until packed into a txt file.
        dframe2csv(args[1][0])
        g_iter = 0
        CH_DATA = {ch: [] for ch in CHANNELS}
        file_iter += 1

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
    parser.add_argument("--fname",
        default=None,
        help="folder name")
    args = parser.parse_args()

    if sys.version_info.major == 3:
    # Set up necessary parameters from command line
        dispatcher = dispatcher.Dispatcher()
        
        if args.option=="print":
            dispatcher.map("/openbci", print_message)
            signal.signal(signal.SIGINT, exit_print)

        # elif args.option=="record":
        #     i = 0
        #     while os.path.exists("osc_record/osc_test%s.txt" % i):
        #         i += 1
        #     filename = "osc_record/osc_test%i.txt" % i
        #     textfile = open(filename, "w")
        #     textfile.write("time,address,ch1,ch2,ch3,ch4\n")
        #     print("Recording to %s" % filename)
        #     dispatcher.map("/openbci", record_to_file)
        #     signal.signal(signal.SIGINT, close_file)
        
        elif args.option=="record":
            dir_path = os.path.join(os.getcwd(), "osc_data", args.fname)
            os.mkdir(dir_path)
            for label in LABELS:
                os.mkdir(os.path.join(dir_path, label))
            dispatcher.map("/openbci", stream_window, dir_path)
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