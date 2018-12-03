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

def predict():
    with open(paths["Log"], 'w') as log:
       log.write(make_header("Starting Script\n"))

    demo_data = pd.read_csv("./predict.csv")

    # Filter the predict data
    demo_data = select_categories(demo_data, CATEGORY)
    demo_data = select_channels(demo_data, CHANNELS)
    #demo_data = select_labels(demo_data, LABELS)
    #demo_data = select_months(demo_data, MONTHS)
    #demo_data = select_days(demo_data, DAYS)
    # train_data = remove_voice(train_data)
    demo_data = demo_data.sample(frac=1).reset_index(drop=True)
    tdcopy = pd.DataFrame(demo_data)

    #demo_data["Label"] = demo_data["Label"].map(labels)
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
    demo_eval_input_fn = create_predict_input_fn(demo_data, 1)

    results = [x for x in classifier.predict(input_fn=demo_eval_input_fn)]
    classes = [x["classes"] for x in results]
    probs = [x["probabilities"] for x in results]
    print(probs)
    result = classes[0]
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