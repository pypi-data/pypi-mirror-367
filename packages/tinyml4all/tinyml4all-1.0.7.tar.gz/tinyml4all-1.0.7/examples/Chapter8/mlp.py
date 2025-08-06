import numpy as np

from tinyml4all.tensorflow import MLP
from tinyml4all.tensorflow.layers import Perceptron
from tinyml4all.datasets import Iris

# Iris is an instance of tinyml4all.tabular.classification.Table
print(Iris)
# instantiate a new network for the Iris dataset
mlp = MLP()
# 8, 16, 24 are the number of perceptrons for each layer
mlp.add(Perceptron(8))
mlp.add(Perceptron(16))
mlp.add(Perceptron(24))
# display network architecture
# X is the input data
# Y are the labels
# task can either be "classification" or "regression"
print(mlp.compile(X=Iris.numeric, Y=Iris.targets.values, task="classification"))
# train neural network and display accuracy plot
mlp.fit(X=Iris.numeric, Y=Iris.targets.values, epochs=50, plot=False)
# print accuracy on the training/validation set
mlp.classification_report()

# export to Arduino-compatible C+
mlp.convert_to("c++", save_to="cpp/IrisMLP.h")

print(
    mlp.predict(
        np.asarray([[5.1, 3.5, 1.4, 0.2], [7.6, 3.0, 6.6, 2.1], [6.8, 2.8, 4.8, 1.0]])
    )
)
