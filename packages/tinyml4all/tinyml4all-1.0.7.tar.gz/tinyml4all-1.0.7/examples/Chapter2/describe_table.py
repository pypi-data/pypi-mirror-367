from tinyml4all.tabular.classification import Table


table = Table.read_csv("sample_data/fruits.csv")

# print the first few rows of table
print(table.head())

# print a few metrics for the table
print(table.describe())

# specify column that contains the labels
table.set_targets(column="fruit")

red = table["r"]
print(red)

table2 = table[["r", "g"]]
print(table2.head())

row = table[0]
print(row)

table2 = table[10:30]
print(table2.head())

# draw scatter plot
table.scatter()

# draw pairplot
table.pairplot()
