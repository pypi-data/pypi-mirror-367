from tinyml4all.time import capture_serial

while True:
    # prompt user for label and duration of sampling
    gesture = input("Which media control gesture is this? ")
    duration = input("How many seconds to capture? ")

    # exit when label or duration is empty
    if not gesture or not duration:
        break

    capture_serial(
        # * is a wildcard character that matches anything
        # on Windows it will look like COM1 or similar
        port="/dev/ttyACM*",
        baudrate=115200,
        # destination file
        save_to=f"sample_data/media-control/{gesture}.csv",
        duration=f"{duration} seconds",
        # name of the columns
        headings="millis, mx, my, mz",
    )
