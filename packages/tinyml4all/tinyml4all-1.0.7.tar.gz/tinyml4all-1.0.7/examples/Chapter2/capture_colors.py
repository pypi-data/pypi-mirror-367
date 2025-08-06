"""
Listing 2-3
Read data from serial port and save to CSV file
"""

from tinyml4all.tabular import capture_serial


while True:
    # prompt user for fruit name and number of samples
    fruit = input("Which fruit is this? ")
    num_samples = input("How many samples to capture? ")

    # exit when fruit or number of samples is blank
    if not fruit or not num_samples:
        break

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
        save_to="fruits.csv",
        # the list of columns to save
        headings="r, g, b, fruit",
        # board only sends r, g, b
        # so we append the fruit manually
        append_values=[fruit],
        num_samples=int(num_samples),
    )
