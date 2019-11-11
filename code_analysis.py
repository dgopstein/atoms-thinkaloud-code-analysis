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
#    Parse survey data
###############################################################################

survey_df = pd.read_csv('survey/Think Aloud Survey Results - Survey.csv')
survey_langs_df = pd.read_csv('survey/Think Aloud Survey Results - Languages.csv')

survey_first_lang_df = survey_langs_df.loc[survey_langs_df.groupby('Subject')['Learned Year'].idxmin()]
survey_first_lang_df.set_index('Subject')


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

# discussion_question_codes.png
chart = sns.countplot(x = 'code',
              data = disc_q_codes_frame,
              order = disc_q_codes_frame['code'].value_counts().index,
              orient = 'v')
chart.set_xticklabels(chart.get_xticklabels(), rotation=90)
plt.gcf().subplots_adjust(bottom=0.5)


#%%############################################################################
#    Correct / Incorrect answers by experience group
###############################################################################
from statistics import mean

snippets_df = pd.DataFrame([s.to_dict() for s in snippets])

subject_groups_df = pd.DataFrame.from_dict({'subject': list(subject_groups.keys()), 'group': list(subject_groups.values())}).set_index('subject')

snippets_df = snippets_df.join(subject_groups_df, on='subject')

snippets_df = snippets_df.replace('Technically Right', 'Right')

snippet_group_groups = snippets_df.groupby(['group', 'answer'], as_index=False).size().to_frame('size').reset_index()
snippet_group_sums = snippet_group_groups.groupby(['group', 'answer']).agg({'size': 'sum'})
snippet_group_rates = snippet_group_sums.groupby(level=0).apply(lambda x: x / float(x.sum()))



#%% Pandas plot
snippet_group_unstacked = snippet_group_rates.unstack()
snippet_group_unstacked.columns = pd.CategoricalIndex(snippet_group_unstacked.columns.values, 
                                  ordered=True, 
                                  categories=[('size', 'Wrong'), ('size', 'Right')])

print(snippet_group_unstacked)
snippet_group_unstacked = snippet_group_unstacked.sort_index(axis=1)

print(snippet_group_unstacked.index)

snippet_group_unstacked = snippet_group_unstacked.reindex(['student', 'user', 'librarian'])
plt.close()
snippet_group_unstacked.plot(kind='bar', stacked=True, color=['orange', 'darkgray'], figsize=(5,6))

plt.savefig('img/group_error_rates.pdf')

#%%############################################################################
#    Error rates by experience years
###############################################################################

subject_answer_sums_df = snippets_df[snippets_df['answer'] != 'Wrong'].groupby('subject')['answer'].count().reset_index()

years_answers_df = subject_answer_sums_df.join(survey_first_lang_df[['Subject', 'Learned Year']].set_index('Subject'), on='subject')

years_answers_df['years_experience'] = years_answers_df.apply(lambda row: 2019-row['Learned Year'], axis=1)

plt.close()
sns.set(rc={'figure.figsize':(5,5)})
years_vs_correctness_plot = sns.scatterplot(x='years_experience', y='answer', data=years_answers_df, s = 70)
years_vs_correctness_plot.set(ylim=(0,8.5),
                              xlabel="Years Programming", ylabel="Correct Answers")
plt.savefig('img/years_vs_correctness.pdf')

#%%############################################################################
#    All unique codes
###############################################################################

from collections import Counter

pprn(Counter([c['content'] for c in codes]))

#%%############################################################################
#    Causes of Confusion
###############################################################################


causes_confusion = [c for c in codes if c['content'] == 'Causes of Confusion']

pprn(causes_confusion)

non_student_wrong_answers = [s for s in snippets if s.answer == 'Wrong' and subject_groups[s.subject] != 'student']

pprn(non_student_wrong_answers)

# The only wrong answer from a librarian was on snippet #115 (users got wrong 61 and 79)
# Find corresponding wrongs among students
matching_student_wrong_answers = [s for s in snippets if s.answer == 'Wrong' and subject_groups[s.subject] == 'student' and s.snippet in [115, 61, 79]]

pprn(matching_student_wrong_answers)

[s for s in snippets if s.answer == 'Wrong' and s.subject == 9112]
