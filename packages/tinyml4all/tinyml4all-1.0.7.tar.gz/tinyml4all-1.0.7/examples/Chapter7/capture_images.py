from tinyml4all.image import capture_serial

while True:
    # prompt user for object name and number of images
    object = input("Which object is this? ")
    num_samples = input("How many images to capture? ")

    # exit if object name or duration is empty
    if not object or not num_samples:
        break

    capture_serial(
        # * is a wildcard character that matches anything
        # on Windows it will look like COM1 or similar
        port="/dev/ttyACM*",
        # must match with the Arduino sketch
        baudrate=115200 * 2,
        save_to=f"objects/{object}",
        num_samples=int(num_samples),
    )
