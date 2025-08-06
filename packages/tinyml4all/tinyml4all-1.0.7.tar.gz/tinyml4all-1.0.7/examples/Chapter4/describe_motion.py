from tinyml4all.time.continuous.classification import TimeSeries


ts = TimeSeries.read_csv_folder("sample_data/motion")
print(ts.head())

# plot data
ts.line(
    title="Continuous motion",
    normalize=True,
    line_palette="magma",
    bg_palette="viridis",
)
