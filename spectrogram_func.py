import subprocess
from scipy.io.wavfile import write
import os, shutil, re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
import librosa
import librosa.display
from helpers import *
from spectrogram_func import *

ROOT = os.getcwd() + "/audio/"
IMG_ROOT = os.getcwd() + "/imgs/"
pattern = "[0-9]{2}_[0-9]{2}"
VALID_LABELS = ["one", "two"]
IMG_EXT = ".png"
VERBOSITY = 1000
NUM_CHANNELS = 22
CATS, MONTHS, DAYS, LABELS, SEQ, SETS = [], [], [], [], [], []
for i in range(1, NUM_CHANNELS+1):
    globals()["PATH{}".format(i)] = []

def preprocess(samples, sample_rate, multiplier=1):
    sr = sample_rate * multiplier
    padded = np.zeros(sr)
    samples = samples[:sr]
    padded[:samples.shape[0]] = samples
    return padded

def make_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)

def process(input_dir, output_dir, overwrite=False):
    items = 0
    created = 0
    found = 0
    plt.ioff()

    for channel in os.listdir(input_dir + "/11_25/one"):
        if channel not in [".DS_Store"] and overwrite:
            created += 1
            sample_rate, samples = wavfile.read(input_dir + "/11_25/one/" +  channel + "/00000.wav")
            samples = preprocess(samples, sample_rate)
            freqs, times, spectrogram = signal.spectrogram(samples, sample_rate)
            S = librosa.feature.melspectrogram(samples, sr=sample_rate, n_mels=128, fmax=512)
            log_S = librosa.power_to_db(S, ref=np.max)
            fig = plt.figure(figsize=(1.28, 1.28), dpi=100, frameon=False)
            ax = plt.Axes(fig, [0., 0., 1., 1.])
            ax.set_axis_off()
            fig.add_axes(ax)
            plt.axis('off')
            librosa.display.specshow(log_S)                     
            plt.savefig(output_dir + "/11_25/one/" +  channel + "/00000")
            plt.close()
    plt.ion()

# def make_df_from_images(image_root):
#     for cat in [d for d in os.listdir(image_root) if "voice" in d]:
#         cat_path = os.path.join(image_root, cat)
#         for date in [d for d in os.listdir(cat_path) if re.match(pattern, d)]:
#             #print("\tProcessing {}".format(date))
#             date_path = os.path.join(cat_path, date)
#             month = int(date[:2])
#             day = int(date[3:])
#             date_count = 0
#             for label in [d for d in os.listdir(date_path) if d in VALID_LABELS]:
#                 label_path = os.path.join(date_path, label)
#                 placeholder = os.path.join(label_path, "ch1")
#                 for image in [f for f in os.listdir(placeholder) if f.endswith(IMG_EXT)]:
#                     date_count += 1
#                     for i in range(1, NUM_CHANNELS+1):
#                         p = os.path.join(label_path, "ch{}".format(i), image)
#                         if os.path.exists(p):
#                             globals()["PATH{}".format(i)].append(p)
#                         else:
#                             globals()["PATH{}".format(i)].append(float('nan'))
#                     CATS.append(cat)
#                     DAYS.append(day)
#                     MONTHS.append(month)
#                     LABELS.append(label)
#                     sequence_number = int(image[:-4])
#                     basenum = sequence_number % 10
#                     SEQ.append(sequence_number)
#                     if basenum < 8:
#                         SETS.append("Training")
#                     elif basenum < 9:
#                         SETS.append("Validation")
#                     else:
#                         SETS.append("Testing")
#             #print("\t\tProcessed {} sequences".format(date_count))
#     d = {
#             "Category":CATS,
#             "Day":DAYS,
#             "Month":MONTHS,
#             "Label":LABELS,
#             "SequenceNumber":SEQ,
#             "Set":SETS
#         }
#     for i in range(1, NUM_CHANNELS+1):
#         d["Path{}".format(i)] = globals()["PATH{}".format(i)]
#     return pd.DataFrame(d)