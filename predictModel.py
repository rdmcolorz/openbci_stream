import os
from pathlib import Path
import IPython.display as ipd
import random
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as py
from IPython import display
import time
from datetime import datetime, timedelta
import tensorflow as tf
import seaborn as sns
import subprocess

# NOTES
CATEGORY = ["no_voice"]
LABELS = ["lights-on", "turn-off"]
CHANNELS = [1, 2, 3, 4]
NUMS = ''.join([str(x) for x in CHANNELS])
MONTHS = [11]
DAYS = [25]
def curr_time():
    return datetime.now() - timedelta(hours=7) # offset from UTC to PST

NOTES = "28x28"
ROOT = os.getcwd() + "/"
if CATEGORY[0] == "no_voice":
    RUN_ROOT = ROOT+"NONVOCAL_RUNS_YN_{:02}_{:02}/".format(MONTHS[0], DAYS[0])
else:
    RUN_ROOT = ROOT+"VOCAL_RUNS_YN_{:02}_{:02}/".format(MONTHS[0], DAYS[0])
RUN_ROOT_LOG = RUN_ROOT+"logs/"
# VARS
target_label = "Label"
id_label = "fname"
VERBOSE = True
DISPLAY = True
TEST = False
TPU = False
RESIZE = True
INPUT_WIDTH = 128
INPUT_HEIGHT = 128
TARGET_WIDTH = 28 if RESIZE else INPUT_WIDTH
TARGET_HEIGHT = 28 if RESIZE else INPUT_HEIGHT
DECAY_RATE = 0.9
IMG_CHANNELS = 3
DROPOUT = 0.4
TYPE = "CNN"
DEFAULT_BS = 128 # default batch size
UNK_DROP_RATE = 1.0 # drop 100% of unknown categories
OUTLIER_PERCENTAGE = 0.1

NUMS = ''.join([str(x) for x in CHANNELS])
MONTHS = [9]
DAYS = [25]

if TEST:
    LEARNING_STEPS = 100
    SPP = 4
    LEARNING_RATE = .05
    BATCH_SIZE = 32
    VERBOSITY = 1000
    TEST_SIZE = 1000
    SHUFFLE_SIZE = 64
else:
    LEARNING_STEPS = 5000
    SPP = 200
    LEARNING_RATE = .025
    BATCH_SIZE = 64
    VERBOSITY = 1000
    SHUFFLE_SIZE = 256
paths = {
    "Training":ROOT+"paths_scaled_combined.csv",
    "Model": ROOT+"demoModelOutliers",
    "Logs":RUN_ROOT_LOG+"{}_{}/".format(NUMS, datetime.strftime(curr_time(), "%b%d%Y_%H%M%S"))
}
paths["Log"] = paths["Logs"] + "log.txt"
#  Create variables for the paths
train_csv = paths["Training"]

# Store the labels to train
all_labels = LABELS
labels = ["one", "two", "silence"]
num_labels = len(labels) - 1
labels = {x[1]:x[0] for x in enumerate(labels)}
reverse_lookup = {labels[k]:k for k in labels}

def curr_time():
    return datetime.now() - timedelta(hours=7) # offset from UTC to PST

ROOT = os.getcwd() + "/"
if CATEGORY[0] == "no_voice":
    RUN_ROOT = ROOT+"NONVOCAL_RUNS_YN_{:02}_{:02}/".format(MONTHS[0], DAYS[0])
else:
    RUN_ROOT = ROOT+"VOCAL_RUNS_YN_{:02}_{:02}/".format(MONTHS[0], DAYS[0])
RUN_ROOT_LOG = RUN_ROOT+"logs/"

# PATHS
paths = {
    "Training":ROOT+"paths_scaled_combined.csv",
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

def make_header(s):
    return ("#" * 42) + ("\n{:^42}\n".format(s)) + ("#" * 42)
    
def print_and_log(s):
    with open(paths["Log"], 'a') as log:
        log.write(str(s))
        log.write("\n")
    print(s)
        
def print_and_log_header(s):
    h = make_header(str(s))
    with open(paths["Log"], 'a') as log:
        log.write(h)
        log.write("\n")
    print(h)

def sec_to_str(secs):
    ms = secs - int(secs)
    days = int(secs // (24 * 3600))
    hours = int((secs % ((24 * 3600))) // 3600)
    minutes = int((secs % 3600) // 60)
    seconds = int(secs % 60)
    return "{:02}:{:02}:{:02}:{:02}.{}".format(days, hours, minutes, seconds, "{:.3}".format(ms)[2:])

def timer(f, *args):
    #print_and_log("Start: {}".format(curr_time()))
    start = time.time()
    result = f(*args)
    end = time.time()
    #print_and_log("End: {}".format(curr_time()))
    #print_and_log("Finished in {}".format(sec_to_str(end - start)))
    return result

def preprocess(samples, sample_rate):
    padded = np.zeros(sample_rate)
    samples = samples[:sample_rate]
    padded[:samples.shape[0]] = samples
    return padded

def select_labels(df, allowed):
    return df[df['Label'].isin(allowed)]
    
def select_categories(df, allowed):
    return df[df['Category'].isin(allowed)]

def select_channels(df, allowed):
    labels = []
    for i in range(1, 9):
        if i not in allowed:
            labels.append("Path{}".format(i))
    return df.drop(labels, axis=1)

def select_days(df, allowed):
    return df[df['Day'].isin(allowed)]

def select_months(df, allowed):
    return df[df['Month'].isin(allowed)]

def select_sets(df, allowed):
    return df[df['Set'].isin(allowed)]

def remove_voice(df):
    return df.drop(["Path4"], axis=1)

def str_to_l(x):
    return [int(n) for n in x if n <= '9' and n >= '0']

count = 0
# def _parse_function(label, *filenames):
#     global count
#     count += 1
#     #if count % VERBOSITY == 0:
#         #print_and_log("\tProcessed {}th image".format(count))
#     expected_shape = tf.constant([1, INPUT_HEIGHT, INPUT_WIDTH, IMG_CHANNELS])
#     image = None
#     for filename in filenames:
#         image_string = tf.read_file(filename)
#         image_decoded = tf.image.decode_image(image_string, channels=IMG_CHANNELS)
#         image_decoded = tf.image.convert_image_dtype(image_decoded, tf.float32)
#         image_decoded = tf.reshape(image_decoded, expected_shape)
#         image_decoded = tf.image.rgb_to_grayscale(image_decoded)
#         if RESIZE:
#             image_decoded = tf.image.resize_bicubic(image_decoded, [TARGET_HEIGHT, TARGET_WIDTH])
#         if image is not None:
#             image = tf.concat([image, image_decoded], 3)
#         else:
#             image = image_decoded
#     return image, label

def _parse_function(label, *filenames):
    global count
    count += 1
    if count % VERBOSITY == 0:
        print_and_log("\tProcessed {}th image".format(count))
    expected_shape = tf.constant([1, INPUT_HEIGHT, INPUT_WIDTH, IMG_CHANNELS])
    image = None
    for filename in filenames:
        image_string = tf.read_file(filename)
        image_decoded = tf.image.decode_image(image_string, channels=IMG_CHANNELS)
        image_decoded = tf.image.convert_image_dtype(image_decoded, tf.float32)
        image_decoded = tf.reshape(image_decoded, expected_shape)
        image_decoded = tf.image.rgb_to_grayscale(image_decoded)
        if RESIZE:
            image_decoded = tf.image.resize_bicubic(image_decoded, [TARGET_HEIGHT, TARGET_WIDTH])
        if image is not None:
            image = tf.concat([image, image_decoded], 3)
        else:
            image = image_decoded
    return image, label

def model_fn(features, labels, mode):
    input_layer = tf.reshape(features, [-1, TARGET_HEIGHT, TARGET_WIDTH, len(CHANNELS)])
    pool = input_layer

    for num_filters in [32, 64]:
        conv = tf.layers.conv2d(
            inputs=pool,
            filters=num_filters,
            kernel_size=[5, 5],
            padding="same",
            activation=tf.nn.relu)
        pool = tf.layers.max_pooling2d(inputs=conv, pool_size=[2, 2], strides=2)

    # Dense Layer
    pool = tf.layers.flatten(pool)
    dense = tf.layers.dense(inputs=pool, units=1024, activation=tf.nn.relu)
    dropout = tf.layers.dropout(inputs=dense, rate=DROPOUT, training=mode == tf.estimator.ModeKeys.TRAIN)

    # Logits Layer
    logits = tf.layers.dense(inputs=dropout, units=num_labels)
    
    predictions = {
        "classes": tf.argmax(input=logits, axis=1),
        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }
    if not TPU:
        tf.summary.histogram("predictions", predictions["probabilities"])
        tf.summary.histogram("classes", predictions["classes"])

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    learning_rate = tf.train.exponential_decay(LEARNING_RATE, tf.train.get_global_step(), SPP, DECAY_RATE, staircase=True)
    
    # Calculate Loss (for both TRAIN and EVAL modes)
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
    predictions["loss"] = loss
    
    # Configure the Training Op (for TRAIN mode)
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
        if TPU:
            optimizer = tf.contrib.tpu.CrossShardOptimizer(optimizer)
        train_op = optimizer.minimize(
            loss=loss,
            global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

    # Add evaluation metrics (for EVAL mode)
    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
            labels=labels, predictions=predictions["classes"])}
    return tf.estimator.EstimatorSpec(
        mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)

def create_training_input_fn(dataset, batch_size, num_epochs=None):
    def _input_fn(num_epochs=None, shuffle=True):
        ds = dataset.batch(batch_size).repeat(num_epochs)
        if shuffle:
            ds = ds.shuffle(SHUFFLE_SIZE)
        feature_batch, label_batch = ds.make_one_shot_iterator().get_next()
        return feature_batch, label_batch
    return _input_fn

def create_predict_input_fn(dataset, batch_size):
    def _input_fn():
        ds = dataset.batch(batch_size)
        feature_batch, label_batch = ds.make_one_shot_iterator().get_next()
        return feature_batch, label_batch
    return _input_fn