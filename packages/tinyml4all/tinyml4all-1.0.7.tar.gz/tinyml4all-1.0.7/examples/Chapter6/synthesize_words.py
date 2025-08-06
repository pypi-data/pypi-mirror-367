from tinyml4all.audio import synthesize_speech

synthesize_speech(
    api_key="fd7c1340f2244847bfc2a9154c8529ef",
    region="westeurope",
    language="en-US",
    save_to="sample_data/synthetic/wakeword",
    text="Hey Arduino",
    # must match with the duration in Listing 6-2
    duration="2 s",
    freq="16 khz",
    num_samples=5,
    # pitch percent variations
    # negative means lower pitch
    pitches=[0, -15, 15],
    # rate percent variations
    # negative means slower
    rates=[0, -10],
)
