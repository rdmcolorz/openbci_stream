import argparse, time, os
import pandas as pd
from osc_helper import *

if sys.version_info.major == 3:
    from pythonosc import dispatcher
    from pythonosc import osc_server
elif sys.version_info.major == 2:
    import OSC

#tf.logging.set_verbosity(tf.logging.ERROR)

# globals ########################
g_iter = 0
sample_data = []
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
    if file_i == 30:
        file_i = 0
    if g_iter == 20:
        sample = np.array(sample_data)
        sample_array = sample.reshape(20,4)
        df = pd.DataFrame(sample_array, columns=["ch1", "ch2", "ch3", "ch4"]) 
        df.to_csv(STREAM_ROOT + str(file_i) + ".txt", ",")
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
        print(" -- OSC LISTENER -- ")
        print('--------------------')
        print("IP:", args.ip)
        print("PORT:", args.port)
        print("ADDRESS:", args.address)
        print('--------------------')
        print("%s option selected" % args.option)

        # connect server
        server = osc_server.OSCUDPServer(
            (args.ip, args.port), dispatcher)
        server.serve_forever()
    else:
        print("Make sure python is version 3 and up")