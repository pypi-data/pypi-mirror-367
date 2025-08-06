# note that the packaged changed from continuous
# to episodic!
from tinyml4all.time.episodic.classification import TimeSeries

ts = TimeSeries.read_csv_folder("sample_data/media-control")

# print autoloaded events
print(list(ts.events))

# run labeling GUI
ts.label_gui()
