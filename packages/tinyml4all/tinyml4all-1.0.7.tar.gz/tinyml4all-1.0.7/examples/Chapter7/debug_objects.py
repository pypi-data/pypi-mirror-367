from tinyml4all.image import debug_serial


debug_serial(
    # * is a wildcard character that matches anything
    port="/dev/ttyACM*",  # must match with the Arduino sketch
    baudrate=115200 * 2,
)
