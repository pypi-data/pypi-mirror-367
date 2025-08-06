from tinyml4all.audio import capture_serial

capture_serial(
    # * is a wildcard match
    port="dev/ttyACM*",
    baudrate=115200 * 2,
    num_samples=30,
    word_duration="2 seconds",
    save_to="sample_data/test",
    mic_frequency="16 khz",
)
