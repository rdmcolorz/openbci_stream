def print_message(*args):
    try:
        current = time.time()
        if sys.version_info.major == 2: #check if python2 
            print("(%f) RECEIVED MESSAGE: %s %s" % (current, args[0], ",".join(str(x) for x in args[2:])))
        elif sys.version_info.major == 3: #check if python3
            print("(%f) RECEIVED MESSAGE: %s %s" % (current, args[0], ",".join(str(x) for x in args[1:])))
    except ValueError: pass

# Clean exit from print mode
def exit_print(signal, frame):
    print("Closing listener")
    sys.exit(0)

# Save recording, clean exit from record mode
def close_file(*args):
    print("\nFILE SAVED")
    textfile.close()
    sys.exit(0)

def channel2wav(ch_data, fname, ch):
    data = np.array(ch_data, dtype='float64')
    data /= np.max(np.abs(data))
    data_resampled = resample(data, len(data) * 40) #since openbci is already sampled at 200
    wavfile.write(fname + ch + '.wav', 201 * 40, data_resampled)

def run_command(command):
	NULL = open(os.devnull, 'w')
	subprocess.run(command, stdout=NULL, stderr=NULL)