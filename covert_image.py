import subprocess
from scipy.io.wavfile import write
import os, shutil, re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
from scipy.signal import resample
from final_predict import predict
import librosa
import librosa.display

def latest_txt_files(path,qty):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if basename.endswith(".txt")]
    s_paths = sorted(paths, key=os.path.getctime, reverse=True)
    ss_paths = sorted(s_paths[:qty])
    return ss_paths

def channel2wav(frame, ch, max_data):
    output_dir='latest_wav'
    data = np.array(frame[ch], dtype='float64')
    #data /= np.max(np.abs(data))
    data /= max_data
    data_resampled = resample(data, len(data) * 40) #since openbci is already sampled at 200
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    name = "%s/%s.wav"%(output_dir,ch)
    wavfile.write(name, 201 * 40, data_resampled)
    #print ("%s file is written"%(name))

def preprocess(samples, sample_rate, multiplier=1):
    sr = sample_rate * multiplier
    padded = np.zeros(sr)
    samples = samples[:sr]
    padded[:samples.shape[0]] = samples
    return padded

def process(input_dir, output_dir):
    items = 0
    created = 0
    found = 0
    plt.ioff()
    chs=['ch1','ch2','ch3','ch4']
    for channel in chs:
        wav_name="%s/%s.wav"%(input_dir,ch)
        sample_rate, samples = wavfile.read(wav_name)
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
        _output_dir = "%s/%s"%(output_dir,channel)
        if not os.path.exists(_output_dir):
            os.makedirs(_output_dir)
        name ="%s/00000.png"%(_output_dir)
        
        #print ("%s file is written"%(name))
        plt.savefig(name)
        plt.close()
    plt.ion()

# replace for folder name that you need
dir=os.getcwd() + "/stream_files"

while (True):
    fls=latest_txt_files(dir,10)
    list_ = []
    print(fls[0])
    for file_ in fls:
        df = pd.read_csv(file_,index_col=None, header=0)
        list_.append(df)

    frame = pd.concat(list_, axis = 0, ignore_index = True)

    # need to be replace with constants obtained from main data
    mx=frame.max()
    cols=['ch1','ch2','ch3','ch4']

    for ch in cols:
        channel2wav(frame,ch,mx[ch])
    process("latest_wav","latest_spec")
    predict()