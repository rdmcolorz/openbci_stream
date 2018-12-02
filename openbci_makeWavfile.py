
# coding: utf-8

# In[1]:

import os, shutil, re
import pandas as pd
from helpers import *
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
from scipy.signal import resample
import librosa
import librosa.display
from pydub import AudioSegment
from datetime import datetime
from helpers import *
get_ipython().magic(u'matplotlib inline')


# In[4]:

# replace this with your root directory
ROOT = os.getcwd() + "/openbci_data/raw_data"
AUD_ROOT = os.getcwd() + "/openbci_data/openbci_to_wav/"
pattern = "[0-9]{2}_[0-9]{2}"

"""
Expected directory structure:
[INSIDE ROOT DIRECTORY]
---- [category] voice, no_voice
-------- [date] 07_02, 07_09, ...
------------ [label] down, go, ...
---------------- [channel] ch1, ch2, ...
-------------------- [wave files] *.wav
"""
# VARS
FNAME = "taylor_11_22"
CSV = "./openbci_data/raw_data/" + FNAME + ".txt"
OUTPUT = AUD_ROOT + FNAME
USELESS = ["na1", "na2", "na3"]
IMG_EXT = ".png"
VERBOSITY = 1000


# In[5]:

# read csv(txt) file write to another csv file to convert into wav files

df = pd.read_csv(CSV, ",")
df = df.drop(columns=USELESS)
df = df.dropna()
ch1_df = df['ch1'].tolist()
ch2_df = df['ch2'].tolist()
ch3_df = df['ch3'].tolist()
ch4_df = df['ch4'].tolist()
# ch3_df = df['ch3'].tolist()

# df['timestamp'] = df['timestamp'].map(timestamp2milsec)
# df['timestamp'] = df['timestamp'].map(lambda x: x - df['timestamp'].iloc[0])


# In[6]:

def channel2wav(ch_data, fname, ch):
    data = np.array(ch_data, dtype='float64')
    data /= np.max(np.abs(data))
    #data_resampled = resample(data, len(data)) #since openbci is already sampled at 200
    wavfile.write(fname + "_" + ch + '.wav', 200, data)
    print("wav file conversion done")


# In[7]:

channel2wav(ch1_df, OUTPUT, "ch1")
channel2wav(ch2_df, OUTPUT, "ch2")
channel2wav(ch3_df, OUTPUT, "ch3")
channel2wav(ch4_df, OUTPUT, "ch4")


# In[ ]:




# In[ ]:



