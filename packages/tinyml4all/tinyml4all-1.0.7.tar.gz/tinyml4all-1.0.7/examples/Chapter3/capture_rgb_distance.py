"""
Listing 3-2
Read data from serial port and save to CSV file
"""

from tinyml4all.tabular import capture_serial


# start the capturing
# will connect to the serial port and read its data
capture_serial(
    # board serial port
    # * is a wildcard match
    # on Windows, this will look like COM1 or similar
    port="/dev/ttyACM*",  #
    # must match with the Arduino sketch
    baudrate=115200,
    # file name where output will be stored
    save_to="sample_data/rgb-distance.csv",
    # the list of columns to save
    headings="r, g, b, distance",
    num_samples=100,
)
