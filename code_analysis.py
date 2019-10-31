import parse_snippets
import pprint
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
plt.ion()

pp = pprint.PrettyPrinter(indent=4)
texts, bookmarks, snippets = parse_interviews()
print() or pp.pprint(snippets)


###############################################################################
#    Heatmap of Correctness vs Confidence
###############################################################################
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


###############################################################################
#    Correctness of NYU students
###############################################################################

nyu_snippets = [x for x in snippets if x.subject in set([4168, 3316, 4281, 9112, 3787])]

nyu_snippets

###############################################################################
#    CSV
###############################################################################

import csv
with open('think_aloud_results.csv', "w") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(['subject', 'start', 'end', 'snippet', 'atom', 'confusingness', 'answer', 'confidence'])
    for s in snippets:
        writer.writerow([s.subject, s.start, s.end, s.snippet, s.atom, s.confusingness, s.answer, s.confidence])



###############################################################################
#    Grouping snippets by code
###############################################################################

pp.pprint(snippets[0].codes)
