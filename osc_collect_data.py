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
label_counter_1 = 0
label_counter_2 = 0
sample_data = []
ch1_data, ch2_data, ch3_data, ch4_data  = [], [], [], []
start = 0
LABELS = ['lights-on', 'turn-off']
 
# Path vars #####################
ROOT = os.getcwd()


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

def stream_window(*args):
    global g_iter, file_i, start, label_counter_1, label_counter_2
    global ch1_data, ch2_data, ch3_data, ch4_data
    if file_i % 2 == 0:
        flag = 1
    else:
        flag = 0

    if g_iter == 0 and flag == 1:
        print(colored("#" * 21 + "\n" + 
                        "#" * 21 + "\n" + 
                        "    TURN OFF \n" +
                        "#" * 21 + "\n" +
                        "#" * 21, 'yellow'))
    elif g_iter == 0 and flag == 0:
        print(colored("#" * 21 + "\n" + 
                        "#" * 21 + "\n" + 
                        "    LIGHTS ON \n" +
                        "#" * 21 + "\n" +
                        "#" * 21, 'green'))
    ch1_data.append(round(args[2],2))
    ch2_data.append(round(args[3],2))
    ch3_data.append(round(args[4],2))
    ch4_data.append(round(args[5],2))
    g_iter += 1
    if g_iter == 400: # number of lines of data until packed into a txt file.
        df = pd.DataFrame(np.column_stack([ch1_data, ch2_data, ch3_data, ch4_data]), 
            columns=['ch1', 'ch2', 'ch3', 'ch4'])
        if flag == 0:
            df.to_csv(args[1][0] + "/lights-on/" + str(label_counter_1) + ".txt", ",")
            label_counter_1 += 1
            print("Produced csv no: {} lable: lights-on".format(file_i))
        elif flag == 1:
            df.to_csv(args[1][0] + "/turn-off/" + str(label_counter_2) + ".txt", ",")
            label_counter_2 += 1
            print("Produced csv no: {} label: turn-off".format(file_i))
        file_i += 1
        g_iter = 0
        ch1_data, ch2_data, ch3_data, ch4_data  = [], [], [], []

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