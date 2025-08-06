import numpy as np

from tinyml4all.tensorflow import CNN2D
from tinyml4all.tensorflow.layers import Conv2D, MaxPooling2D, Perceptron
from tinyml4all.datasets import Pets

cnn = CNN2D(input_shape=(48, 48))
# example of Conv2 + max pooling
# 8 is the number of kernels
cnn.add(Conv2D(8, kernel_size=3))
cnn.add(MaxPooling2D())
# example of Conv2D with stride
cnn.add(Conv2D(16, kernel_size=3, strides=2))
# stride & max pooling
# (result is ¼ the size)
cnn.add(Conv2D(24, kernel_size=3, strides=2))
cnn.add(MaxPooling2D())
# fully connected layer before output
cnn.add(Perceptron(32))
# display network architecture
print(cnn.compile(Pets.X, Pets.Y))

# train neural network and display accuracy plot
cnn.fit(Pets.X, Pets.Y, epochs=50, plot=False)
# print accuracy on the validation set
print(cnn.classification_report())

pred = cnn.predict(Pets.X)

for x, a, b in zip(Pets.X, Pets.Y, pred):
    if a == 1 and b[1] > 0.8:
        print((x * 255).astype(np.uint8).flatten().tolist())
        break

# export to Arduino-compatible C+
cnn.convert_to("c++", class_name="CNN2D", save_to="cpp/PetsCNN2D.h")
