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
