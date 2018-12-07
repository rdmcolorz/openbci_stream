# OpenBCI data prediction stream
- This is the repo to that takes OpenBCI data with the networking widget and uses OSC to stream data to the macbook.

#### `split_to_files.py`
- Reads in the OpenBCI from the OSC server, takes 20 data points and converts them to csv files continuously up to 30 files,
and then rewrites them.

#### `convert_image.py`
- Run this code to grab data from the chunks `split_to_files.py` outputs, and stiches 10 files together to produce a second of data
OpenBCI transfers to the macbook through BLE (sample rate : 200hz).
- Need to delete the `downsampled` folder to start running this code since the command `ffmpg` stops running when there are already files 
in the directory, will try to fix this next. While running the code `downsampled` will delete itself when done predicting so the code
will keep running.