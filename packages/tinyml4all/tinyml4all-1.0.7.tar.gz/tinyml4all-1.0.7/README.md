Python library for the book [TinyML Quickstart](https://link.springer.com/book/10.1007/979-8-8688-1294-1).
Contains code and examples.

## Installation

```bash
pip install tinyml4all
```

## Usage

For a complete list of the examples, refer to the book. Here's one that
classifies a tabular dataset and exports a C++ header file for Arduino:

```python
from tinyml4all.tabular.classification import Table, Chain
from tinyml4all.tabular.features import Scale
from tinyml4all.tabular.classification.models import RandomForest


table = Table.read_csv("sample_data/fruits.csv").set_targets(column="fruit")

# print a description of the parameters you can set
# on the given classifier
print(help(RandomForest))

# train classifier and make predictions
rf = RandomForest(n_estimators=20)
table2 = rf(table)

# table.full() prints the data + true labels + predicted labels
print(table2.full())
print(table2.classification_report())

# create a chain of preprocessing and classification
chain = Chain(Scale(), RandomForest(n_estimators=20))
table2 = chain(table)
print(table2.classification_report())

# export for Arduino
chain.convert_to("c++", class_name="FruitChain", save_to="sample_data/FruitChain.h")
```