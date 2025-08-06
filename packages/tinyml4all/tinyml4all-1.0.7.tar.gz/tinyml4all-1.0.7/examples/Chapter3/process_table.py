from tinyml4all.tabular.classification import Table, Chain
from tinyml4all.tabular.features import Monotonic, Multiply, Scale

table = Table.read_csv("sample_data/rgb-distance.csv").set_targets(column="distance")

# apply the square and cube mapping to all columns
square_and_cube = Monotonic(functions="square, cube")
# apply all the mappings only to the "r" column
only_r = Monotonic(columns="r")
# apply all mappings to all columns
monotonic = Monotonic()
# run the transform on the table
table2 = monotonic(table)
print(table2.describe())

# assume the people.csv files contains width (w), height (h)
# and BMI of a group of people
table = Table.read_csv("sample_data/people.csv")
# if you omit the columns parameter,
# all columns will be considered
mult = Multiply(columns=["Height", "Weight"])
table2 = mult(table)
print(table2.describe())

# chain operations
chain = Chain(
    Scale(method="maxabs"),
    Monotonic(functions="square, cube"),
    Multiply(columns=["Height", "Weight"]),
)
table2 = chain(table)
print(table2.describe())
