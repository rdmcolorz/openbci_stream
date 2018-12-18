# OpenBCI data prediction stream

- What we are doing is using OpenBCI to collect data with its GUI networking widget and uses OSC to stream data, and using that data from the vocal cords and translate it to words and sentences.
- Uses the python-osc library to communicate with the OpenBCI device.
- Since I'm using synchronous streaming, which is not the most optimal way to stream data, but what I want to do is to get it to work first without losing any data from the device.

- While using the python-osc library, had a problem where I was getting duplicate data from the device, and after I restart the OpenBCI GUI, the data would stream properly, so reminder is to restart the GUI whenever you want to stream or record data.

- Device used: [OpenBCI Ganglion](http://docs.openbci.com/Tutorials/02-Ganglion_Getting%20Started_Guide)

#### `split_to_files.py`
- Reads in the OpenBCI from the OSC server, takes 20 data points and converts them to csv files continuously up to 30 files,
and then rewrites them.

#### Additional parameters
- `--option` 
  - `print` : prints the data streaming from the device.
  - `record` : records the data from the device to a txt file
  - `predict` : runs the data through a CNN model and predicts what the data means. (ex: 'yes' or 'no')

#### `convert_image.py`
- Run this code to grab data from the chunks `split_to_files.py` outputs, and stiches 10 files together to produce a second of data
OpenBCI transfers to the macbook through BLE (sample rate : 200hz).
- Need to delete the `downsampled` folder to start running this code since the command `ffmpg` stops running when there are already files 
in the directory, will try to fix this next. While running the code `downsampled` will delete itself when done predicting so the code
will keep running.
