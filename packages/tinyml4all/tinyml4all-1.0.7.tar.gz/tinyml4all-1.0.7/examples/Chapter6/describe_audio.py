from tinyml4all.audio import Album

album = Album.read_wav_folders(
    "sample_data/wakeword",
    "sample_data/unknown",
    "sample_data/synthetic/wakeword",
    "sample_data/synthetic/unknown",
)

# plot samples (overlapping)
album.overlap_plot(palette="magma", samples_per_class=50, points_per_sample=1_000)

# plot samples (sequential)
album.sequential_plot(palette="viridis", samples_per_class=10, points_per_sample=1_000)
