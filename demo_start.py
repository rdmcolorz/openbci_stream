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

# make images VARS  #############
pattern = "[0-9]{2}_[0-9]{2}"
IMG_EXT = ".png"
VERBOSITY = 1000
CHANNELS = [1,2,3,4]
NUM_CHANNELS = 22
CATS, MONTHS, DAYS, LABELS, SEQ, SETS = [], [], [], [], [], []
CATEGORY = ["no_voice"]
LABELS = ["one","two"]
NUMS = ''.join([str(x) for x in CHANNELS])
MONTHS = [11]
DAYS = [25]
REWRITE = True # rewrites the spectrograms for every recording use False to debug certain spectrograms

# Path vars #####################
ROOT = os.getcwd()
AUDIO_ROOT = os.getcwd() + "/audio/"
IMG_ROOT = os.getcwd() + "/imgs/"
OUTPUT = os.getcwd() + "/predict.csv"
paths = {
    "Training":AUDIO_ROOT+"paths_scaled_combined.csv",
    "Model": ROOT+"demoModelOutliers",
    "Logs":RUN_ROOT_LOG+"{}_{}/".format(NUMS, datetime.strftime(curr_time(), "%b%d%Y_%H%M%S"))
}
paths["Log"] = paths["Logs"] + "log.txt"
if not os.path.isdir(RUN_ROOT):
    os.mkdir(RUN_ROOT)
if not os.path.isdir(RUN_ROOT_LOG):
    os.mkdir(RUN_ROOT_LOG)
if not os.path.isdir(paths["Logs"]):
    os.mkdir(paths["Logs"])

#################################

def transform_data(sample_data):
    sample_array = np.array(sample_data)

    sample_array = sample_array.reshape(201,4)
    df = pd.DataFrame(sample_array, columns=["ch1", "ch2", "ch3", "ch4"])
    print(df.head(5))
    g_iter = 0
    sample_data = []
    print("Start Prediction!")
    for i in range(1,5):
        ch_df = df["ch%i" % i].tolist()
        channel2wav(ch_df, AUDIO_ROOT + "no_voice/11_25/one/ch%i/" % i, "00000")
    ## make spectrograms
    if not os.path.isdir(IMG_ROOT):
        os.mkdir(IMG_ROOT)
    process(AUDIO_ROOT + "no_voice", IMG_ROOT + "no_voice", overwrite=REWRITE) 
    

def stream_window(*args):
    #try:
    global g_iter
    global sample_data
    global start
    global process_nb
    if g_iter == 0:
        start = timeit.default_timer()
    if g_iter == 201:
        transform_data(sample_data)
        #predict_fn()
        stop = timeit.default_timer()
        print("Prediction Done!")
        print("Prediction time : {:0.2f} seconds\n".format(stop - start))
    for x in args[1:]:
        sample_data.append(x)
    g_iter += 1
    #except ValueError: pass

def predict():
        # overwrite parameter overwrites the spectrogram with new ones

    # df_train = make_df_from_images(IMG_ROOT)
    # df_train.to_csv(OUTPUT, index=False)

    with open(paths["Log"], 'w') as log:
       log.write(make_header("Starting Script\n"))

    #Create variables for the paths
    # train_csv = paths["Training"]

    # Store the labels to train
    # all_labels = LABELS
    # labels = ["one", "two"]
    # num_labels = len(labels) - 1
    # labels = {x[1]:x[0] for x in enumerate(labels)}
    # reverse_lookup = {labels[k]:k for k in labels}

    demo_data = pd.read_csv("./predict.csv")

    # Filter the predict data
    demo_data = select_categories(demo_data, CATEGORY)
    demo_data = select_channels(demo_data, CHANNELS)
    demo_data = select_labels(demo_data, LABELS)
    #demo_data = select_months(demo_data, MONTHS)
    #demo_data = select_days(demo_data, DAYS)
    # train_data = remove_voice(train_data)
    demo_data = demo_data.sample(frac=1).reset_index(drop=True)
    tdcopy = pd.DataFrame(demo_data)
    demo_data["Label"] = demo_data["Label"].map(labels)
    # if VERBOSE:
    #     print_and_log_header("TRAIN DATA")
    #     print_and_log(demo_data.describe())
    #     print_and_log(demo_data.head(10))

    # # Separate Labels
    demo_labels = demo_data.pop(target_label)
    img_paths = ["Path{}".format(channel) for channel in CHANNELS]
    demo_data = demo_data[img_paths]

    # Vectors of filenames.
    t_f, v_f, s_f = [], [], []
    for i in range(1, 1 + len(CHANNELS)):
        channel = CHANNELS[i-1]
        l = "Path{}".format(channel)
        t_f.append(tf.constant(demo_data[l]))

    # `labels[i]` is the label for the image in `filenames[i]
    # Vectors of labels
    demo_labels = tf.constant(demo_labels)

    # Make datasets from filenames and labels
    demo_data = tf.data.Dataset.from_tensor_slices((demo_labels, *t_f))
    demo_data = timer(lambda: demo_data.map(_parse_function))
    # Create the Estimator
    classifier = tf.estimator.Estimator(model_fn=model_fn, model_dir=paths["Model"])
    # Create the input functions.
    demo_eval_input_fn = create_predict_input_fn(demo_data, DEFAULT_BS)

    results = [x for x in classifier.predict(input_fn=demo_eval_input_fn)]
    classes = [x["classes"] for x in results]
    probs = [x["probabilities"] for x in results]
    #print(probs)

    result = classes[0]
    print(probs)
    # Turn wemo device on and off
    on = "wemo switch \"cerebro plug\" on"
    off = "wemo switch \"cerebro plug\" off"
    on_off = [on, off]

    #print(result)
    if result < 2:
        #subprocess.run(on_off[result], shell=True)
        if result == 0 and probs[0][result] > 0.7:
            print("-" * 21 + "\n     Lights ON!\n" + "-" * 21)
        elif result == 1 and probs[0][result] > 0.7:
            print("-" * 21 + "\n     Lights OFF!\n" + "-" * 21)
        else:
            print("-" * 21 + "\nNothing Happened :(\n" + "-" * 21)
    else:
        print("-" * 21 + "\n Nothing Happened !\n" + "-" * 21)

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

        elif args.option=="predict":
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
