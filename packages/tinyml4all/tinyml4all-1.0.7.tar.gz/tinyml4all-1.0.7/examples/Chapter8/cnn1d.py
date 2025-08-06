from tinyml4all.tensorflow import CNN1D
from tinyml4all.tensorflow.layers import Conv1D, Perceptron
from tinyml4all.time.continuous.classification import TimeSeries

ts = TimeSeries.read_csv_folder("../Chapter4/sample_data/motion")
ts.label_from_source()
X, Y = ts.as_windows(duration="1s", shift="250ms")
cnn = CNN1D()
# refer to section "2D Convolutional networks" for what stride is
cnn.add(Conv1D(8))
cnn.add(Conv1D(16))
cnn.add(Conv1D(24, kernel_size=3, strides=2))
cnn.add(Perceptron(32))
# display network architecture
print(cnn.compile(X, Y, task="classification"))
# train neural network and display accuracy plot
cnn.fit(X, Y, epochs=50, plot=True)
# print accuracy on the validation set
print(cnn.classification_report())

# export to Arduino-compatible C+
cnn.convert_to("c++", save_to="cpp/MotionCNN.h")
