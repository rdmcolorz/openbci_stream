import argparse, time, atexit, signal, time
import os, sys, subprocess, threading, shutil
import pandas as pd
#import pygame
import tensorflow as tf
from model_func import *
from predictModel import _parse_function
from termcolor import colored

tf.logging.set_verbosity(tf.logging.ERROR)

# make images VARS  #############
pattern = "[0-9]{2}_[0-9]{2}"
VERBOSITY = 1000
CHANNELS = [1,2,3,4]
CATEGORY = ["no_voice"]
LABELS = ["lights-on", "turn-off", "---"]
ENCODE_LABELS = {x[1]:x[0] for x in enumerate(LABELS)}
NUMS = ''.join([str(x) for x in CHANNELS])
target_label = "Label"
POOL = 0
lights_on = 0
turn_off = 0
silence = 0
on = "wemo switch \"cerebro plug\" on"
off = "wemo switch \"cerebro plug\" off"

# Path vars #####################
ROOT = os.getcwd()
AUDIO_ROOT = os.getcwd() + "/audio/"
IMG_ROOT = os.getcwd() + "/imgs/"
OUTPUT = os.getcwd() + "/predict.csv"
paths = {
    "vocal": ROOT+"/models/vocal_model",
    "subvocal": ROOT + "/models/subvocal_model",
}
DEFAULT_BS = 1

#################################

def predict(model):
    global POOL
    global lights_on
    global turn_off
    global silence 

    demo_data = pd.read_csv("./predict.csv")
    demo_data["Label"] = demo_data["Label"].map(ENCODE_LABELS)
    demo_labels = demo_data.pop(target_label)
    img_paths = ["Path{}".format(channel) for channel in CHANNELS]
    demo_data = demo_data[img_paths]

    # Vectors of filenames.
    t_f = []
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
    classifier = tf.estimator.Estimator(model_fn=model_fn, model_dir=paths[model])
    # Create the input functions.
    demo_eval_input_fn = create_predict_input_fn(demo_data, DEFAULT_BS)
    results = [x for x in classifier.predict(input_fn=demo_eval_input_fn)]
    classes = [x["classes"] for x in results]
    probs = [x["probabilities"] for x in results]
    result = classes[0]
    print("lights-on :{:f}, turn-off : {:f}, silence : {:f}".format(probs[0][0], probs[0][1], probs[0][2]))

    if result == 0:
        lights_on += 1
    elif result == 1:
        turn_off += 1
    else:
        silence += 1
    POOL += 1
    if POOL == 4:
        if lights_on in (2,3,4):
            print(colored("-" * 21 + "\n     Lights ON!\n" + "-" * 21, 'green'))
            #subprocess.run(on, shell=True) # triggers the wemo swithces
        elif turn_off in (2,3,4): # and probs[0][result] > 0.7:
            print(colored("-" * 21 + "\n     Turned OFF!\n" + "-" * 21, 'yellow'))
            #subprocess.run(off, shell=True) # triggers the wemo swithces
        else:
            print(colored("-" * 21 + "\n..... Silence .....\n" + "-" * 21, 'red'))
        POOL = 0
        lights_on = 0
        turn_off = 0
        silence = 0
    # if ans ==  # and probs[0][result] > 0.9:
    #     print(colored("-" * 21 + "\n     Lights ON!\n" + "-" * 21, 'green'))
    #     subprocess.run(on, shell=True) # triggers the wemo swithces
    # elif result == 1 # and probs[0][result] > 0.7:
    #     print(colored("-" * 21 + "\n     Turned OFF!\n" + "-" * 21, 'yellow'))
    #     subprocess.run(off, shell=True) # triggers the wemo swithces
    # else:
    #     print(colored("-" * 21 + "\n..... Silence .....\n" + "-" * 21, 'red'))