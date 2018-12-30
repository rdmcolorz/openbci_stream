import argparse, time, os, sys
import pandas as pd
import numpy as np
from osc_helper import *
import signal
from termcolor import colored
if sys.version_info.major == 3:
    from pythonosc import dispatcher
    from pythonosc import osc_server
elif sys.version_info.major == 2:
    import OSC

#tf.logging.set_verbosity(tf.logging.ERROR)

# globals ########################
g_iter = 0
file_i = 0
sample_data = []
CHANNELS = ['ch1', 'ch2', 'ch3', 'ch4']
CH_DATA = {ch: [] for ch in CHANNELS}
NB_CHANNELS = len(CH_DATA.keys())
INTERVAL = 2 # seconds to record of each label
start = 0
 
# Path vars #####################
ROOT = os.getcwd()
STREAM_ROOT = os.getcwd() + "/stream_files/"

# trying to make stream_window faster so we don't get duplicate data, 
# but wonder if it is the problem at all though.
# needs testing.

def record_to_file(*args):
    # global checker_value_1
    # global checker_value_2
    # global checker_value_3
    
    # if args[2] != checker_value_1 and args[2] != checker_value_2 and args[2] != checker_value_3:
    textfile.write(str(time.time()) + ",")
    textfile.write(",".join(str(x) for x in args))
    textfile.write("\n")
    # checker_value_3 = checker_value_2
    # checker_value_2 = checker_value_1
    # checker_value_1 = args[2]

# Save recording, clean exit from record mode
def close_file(*args):
    print("\nFILE SAVED")
    textfile.close()
    sys.exit(0)

def stream_window(*args):
    global g_iter, file_i, start
    global ch1_data, ch2_data, ch3_data, ch4_data
    if g_iter == 0 and file_i % 2 == 0:
        print(colored("#" * 21 + "\n" + 
                        "#" * 21 + "\n" + 
                        "    Say command : \n" +
                        "#" * 21 + "\n" +
                        "#" * 21, 'yellow'))

    for x in range(1, NB_CHANNELS + 1):
        CH_DATA['ch{}'.format(x)].append(round(args[x], 2))

    g_iter += 1
    if file_i == 10: # the number of files until it overwrites the first one.
        file_i = 0
    if g_iter == 200 * INTERVAL: # number of lines of data until packed into a txt file.
        df = pd.DataFrame(CH_DATA)
        if file_i % 2 == 0:
            df.to_csv(STREAM_ROOT + str(file_i) + ".txt", ",")
            print(max(df['ch2']))
            print("Produced csv no: {}".format(file_i))
        file_i += 1
        g_iter = 0
        CH_DATA = {ch: [] for ch in CHANNELS}

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