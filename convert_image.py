import subprocess, argparse
from scipy.io.wavfile import write
import os, shutil, re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
from final_predict import predict
from voice_predict import voice_predict
import librosa
import librosa.display
from termcolor import colored
import time

def latest_txt_files(path,qty):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if basename.endswith(".txt")]
    s_paths = sorted(paths, key=os.path.getctime, reverse=True)
    ss_paths = sorted(s_paths[:qty], key=os.path.getctime)
    return ss_paths

def channel2wav(frame, ch):
    ch1_max = 130
    ch2_max = 400
    ch3_max = 300
    ch4_max = 100
    output_dir='latest_wav'
    data = np.array(frame[ch], dtype='float64')
    #data /= np.max(np.abs(data))
    if ch == "ch1":
        data /= ch1_max
    if ch == "ch2":
        data /= ch2_max
    if ch == "ch3":
        data /= ch3_max
    if ch == "ch4":
        data /= ch4_max
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    name = "%s/%s.wav"%(output_dir,ch)
    wavfile.write(name, 200, data)
    #print ("%s file is written"%(name))

def preprocess(samples, sample_rate, multiplier=1):
    sr = sample_rate * multiplier
    padded = np.zeros(sr)
    samples = samples[:sr]
    padded[:samples.shape[0]] = samples
    return padded

def run_command(command):
	NULL = open(os.devnull, 'w')
	subprocess.run(command, stdout=NULL, stderr=NULL)

def downsample(audio_path, sample_rate=8000):
	new_audio_path = os.path.join(os.getcwd() + "/downsampled")
	if not os.path.isdir(new_audio_path):
		os.mkdir(new_audio_path)
	for wavfile in [f for f in os.listdir(audio_path) if f.endswith(".wav")]:
		original_filepath = os.path.join(audio_path, wavfile)
		new_filepath = os.path.join(new_audio_path, wavfile)
		command = ["ffmpeg", "-i", original_filepath, "-ar", str(sample_rate), new_filepath]
		#print("\tDownsampling {} to {}Hz".format(original_filepath, sample_rate))
		run_command(command)

def pure_process(input_dir, output_dir):
    plt.ioff()
    chs=['ch1','ch2','ch3','ch4']

    for channel in chs:
        wav_name="%s/%s.wav"%(input_dir,channel)
        sample_rate, samples = wavfile.read(wav_name)
        samples = preprocess(samples, sample_rate)
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
        plt.savefig(name)
        plt.close()
    plt.ion()

def process(input_dir, output_dir):
    plt.ioff()
    chs=['ch1','ch2','ch3','ch4']

    for channel in chs:
        wav_name="%s/%s.wav"%(input_dir,channel)
        sample_rate, samples = wavfile.read(wav_name)
        dataPts = len(samples)
        window = 12000
        difference = 4000
        chunk = int(difference / 5)
        changed_1 = samples[chunk:window+chunk * 2]
        changed_2 = preprocess(changed_1, sample_rate)

        S = librosa.feature.melspectrogram(changed_2, sr=sample_rate, n_mels=128, fmax=512)
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


if __name__ == "__main__":
    # replace for folder name that you need
    dir=os.getcwd() + "/stream_files"
    AUDIO = os.getcwd() + "/latest_wav/"
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",
        default="vocal", 
        help="The type of model, vocal for voice, subvocal for subvocal")
    args = parser.parse_args()
        
    while (True):
        print(colored("-" * 21 + "\nSay command : \n" + "-" * 21, 'white'))
        fls=latest_txt_files(dir,20)
        list_ = []
        for file_ in fls:
            df = pd.read_csv(file_,index_col=None, header=0)
            list_.append(df)
        #print(list_)
        frame = pd.concat(list_, axis = 0, ignore_index = True)
        # need to be replace with constants obtained from main data
        cols=['ch1','ch2','ch3','ch4']
        for ch in cols:
            channel2wav(frame,ch)
        downsample(AUDIO, 8000)
        process("downsampled","latest_spec")
        if args.model == 'vocal':
            voice_predict()
        elif args.model == 'subvocal':
            predict()
        shutil.rmtree(os.getcwd() + "/downsampled")