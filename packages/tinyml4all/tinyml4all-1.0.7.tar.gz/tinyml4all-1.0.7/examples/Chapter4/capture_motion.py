from tinyml4all.time import capture_serial

while True:
    gesture = input("Which gesture is this? ")
    duration = input("How many seconds to capture? ")

    if not gesture or not duration:
        break

    capture_serial(
        # * is a wildcard character
        port="/dev/ttyACM*",  # match with Arduino sketch
        baudrate=115200,
        duration=f"{duration} seconds",
        save_to=f"sample_data/episodic/{gesture}.csv",
        # must match the order in the Arduino sketch!
        headings="millis, ax, ay, az, gx, gy, gz",
    )
