from tinyml4all.tabular.classification import Table, Chain
from tinyml4all.tabular.features import Scale, Select


table = Table.read_csv("sample_data/fruits.csv").set_targets(column="fruit")

# apply minmax scaling
minmax = Scale(method="minmax")
table2 = minmax(table)
print(table2.describe())

# apply feature selection
select = Select(sequential="auto", direction="forward")
select = Select(univariate=1)
select = Select(rfe=1)
select = Select(include=["b"])
select = Select(rfe=2, exclude=["g"])

table2 = select(table)
print(table2.describe())

# chain operations
chain = Chain(minmax, select)
table2 = chain(table)
print(table2.describe())
