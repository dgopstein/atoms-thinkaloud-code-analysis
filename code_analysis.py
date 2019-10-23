import parse_snippets
import pprint
import numpy as np
import pandas as pd
import seaborn as sns

snippets = parse_interviews()
print() or pp.pprint(snippets)


X = np.linspace(0, 1, 101)
Y = np.linspace(0, 1, 101)

data = np.zeros((101, 101))

# or use meshgrid instead
for i, x in enumerate(X):
    for j, y in enumerate(Y):
        data[i, j] = some_function(x, y)

df = pd.DataFrame(data, index=Y, columns=X)

sns.heatmap(df)
