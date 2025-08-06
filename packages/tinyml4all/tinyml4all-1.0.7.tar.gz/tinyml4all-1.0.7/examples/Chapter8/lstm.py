from tinyml4all.tensorflow import RNN
from tinyml4all.tensorflow.layers import LSTM, Perceptron
from tinyml4all.time.continuous.classification import TimeSeries

ts = TimeSeries.read_csv_folder("../Chapter4/sample_data/motion")
ts.label_from_source()
# convert TimeSeries to X and Y training data for NN
X, Y = ts.as_windows(duration="1s", shift="250ms")
rnn = RNN()
# two LSTM layers with 6 neurons + one Fully connected
rnn.add(LSTM(12))
rnn.add(LSTM(12))
rnn.add(Perceptron(16))
# display network architecture
print(rnn.compile(X, Y, task="classification"))

# train neural network and display accuracy plot
rnn.fit(X, Y, epochs=50, plot=True)
# print accuracy on the validation set
print(rnn.classification_report())

# export to Arduino-compatible C+
rnn.convert_to("c++", class_name="LSTM", save_to="cpp/MotionLSTM.h")
