from tinyml4all.tabular.regression import Table


table = Table.read_csv("sample_data/rgb-distance.csv").set_targets(column="distance")

# print the first few rows of table
print(table.head())

# print a few metrics for the table
print(table.describe())

# plot single column vs ground truth
table.scatter(column="r")

# plot all columns vs ground truth
table.scatter()
