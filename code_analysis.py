import parse_snippets
import pprint
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
plt.ion()

pp = pprint.PrettyPrinter(indent=4)
snippets = parse_snippets.parse_interviews()
print() or pp.pprint(snippets)


X = np.linspace(0, 1, 2)
Y = np.linspace(1, 6, 6)

data = np.zeros((6, 2))

for snippet in snippets:
    x = 1 if snippet.answer == 'Wrong' else 0
    y = snippet.confidence - 1

    data[y, x] += 1

    data

df = pd.DataFrame(data)

plt.close()
hm = sns.heatmap(df)
hm.invert_yaxis()

