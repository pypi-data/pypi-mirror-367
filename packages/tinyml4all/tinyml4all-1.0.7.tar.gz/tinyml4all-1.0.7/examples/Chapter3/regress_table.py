from tinyml4all.tabular.regression import Table, Chain
from tinyml4all.tabular.features import Scale, Monotonic, Select
from tinyml4all.tabular.regression.models import (
    Linear,
    Ridge,
    Lasso,
    RandomForest,
    DecisionTree,
)


table = Table.read_csv("sample_data/rgb-distance.csv").set_targets(column="distance")

# print a description of the parameters you can set
# on the given classifier
print(help(RandomForest))

linear = Linear()
ridge = Ridge()
lasso = Lasso()
tree = DecisionTree()
rf = RandomForest()
# apply any of the models above
table2 = linear(table)
# get metrics
print(table2.regression_report())

# create a chain of preprocessing and regression
chain = Chain(
    Scale("minmax"), Monotonic(), Select(rfe=5), RandomForest(n_estimators=20)
)
table2 = chain(table)
print(table2.regression_report())

print("chain", chain)

# export for Arduino
chain.convert_to(
    "c++", class_name="DistanceChain", save_to="sample_data/DistanceChain.h"
)
