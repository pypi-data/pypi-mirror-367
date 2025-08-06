from tinyml4all.datasets import Iris
from tinyml4all.tabular.features import BoxCox, YeoJohnson

print(Iris.describe())
# Iris.scatter(title="Original")

# Box-Cox power transformation
boxcox = BoxCox()
Iris2 = boxcox(Iris)
print(Iris2.describe())
print(boxcox.convert_to("c++"))
# Iris2.scatter(title="Box-Cox")

# Yeo-Johnson power transformation
yeo = YeoJohnson()
Iris3 = yeo(Iris)
print(Iris3.describe())
# Iris3.scatter(title="Yeo-Johnson")
print(yeo.convert_to("c++"))
