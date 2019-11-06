import os, sys


#abspath = os.path.abspath(__file__)
#dname = os.path.dirname(abspath)
dname = '/Users/dgopstein/nyu/confusion/think-aloud/code_analysis'
os.chdir(dname)
sys.path.insert(0, dname)

import parse_snippets
import extract_rtf
import pprint
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


plt.ion()
pp = pprint.PrettyPrinter(indent=4)
pprn = pp.pprint

texts, bookmarks, snippets = parse_snippets.parse_interviews()
codes = [b for b in bookmarks if parse_snippets.is_code(b)]
overlaps = extract_rtf.all_overlaps(bookmarks)
print() or pp.pprint(snippets)
snippets[0].discussion_codes

#%%############################################################################
#    Participant Groups
###############################################################################

subject_groups = {4168: 'student',
 3316: 'student',
 4281: 'student',
 9112: 'student',
 3787: 'student',
 6061: 'user',
 8888: 'user',
 4304: 'user',
 1879: 'user',
 1157: 'librarian',
 7640: 'librarian',
 4642: 'librarian',
 8697: 'librarian',
 1867: 'librarian'}

#%%############################################################################
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


#%%#############################################################################
#    Correctness of NYU students
###############################################################################

nyu_snippets = [x for x in snippets if x.subject in set([4168, 3316, 4281, 9112, 3787])]

nyu_snippets

#%%############################################################################
#    CSV
###############################################################################


import csv
with open('tmp/think_aloud_results.csv', "w") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(['subject', 'start', 'end', 'snippet', 'atom', 'confusingness', 'answer', 'confidence'])
    for s in snippets:
        writer.writerow([s.subject, s.start, s.end, s.snippet, s.atom, s.confusingness, s.answer, s.confidence])



#%%############################################################################
#    Grouping snippets by code
###############################################################################

pp.pprint(snippets[0].codes)


#%%############################################################################
#    All subjects' discussion questions
###############################################################################
#%%

def removekey(d, key):
    r = dict(d)
    if r.get(key):
        del r[key]
    return r

disc_qs = [{**c, 'snippet': s.snippet} for s in snippets for c in s.discussion_codes if c['content'] == 'Discussion Question']

disc_q_codes = []
for q in disc_qs:
    overlapping_codes = [code for code in codes if extract_rtf.overlap_bkmk(code, q) > 0]
    disc_q_codes.append({**removekey(q, 'text'), 'codes': [c['content'] for c in overlapping_codes]})

disc_q_codes[0:2]

flat_disc_q_codes = [c for cs in disc_q_codes for c in cs['codes']]

disc_q_codes_frame = pd.DataFrame({'code':flat_disc_q_codes})

plt.close()
#chart = sns.catplot(x="code", kind="count", palette="ch:.25", data=disc_q_codes_frame)
chart = sns.countplot(x = 'code',
              data = disc_q_codes_frame,
              order = disc_q_codes_frame['code'].value_counts().index,
              orient = 'v')
chart.set_xticklabels(chart.get_xticklabels(), rotation=90)
plt.gcf().subplots_adjust(bottom=0.5)


