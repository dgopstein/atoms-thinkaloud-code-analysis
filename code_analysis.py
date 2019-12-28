import os, sys

#abspath = os.path.abspath(__file__)
#dname = os.path.dirname(abspath)
dname = '/Users/dgopstein/nyu/confusion/think-aloud/code_analysis'
os.chdir(dname)
sys.path.insert(0, dname)

import parse_snippets
import extract_rtf
import lib
import io
import pprint
import numpy as np
import scipy
import pandas as pd
import seaborn as sns
import matplotlib as mpl
from matplotlib import pyplot as plt
import collections
import statsmodels.api as sm
from statsmodels.formula.api import ols
import math

#%%############################################################################
#    Library
###############################################################################

#%%############################################################################
#    Initialization
###############################################################################

plt.ion()
pp = pprint.PrettyPrinter(indent=4)
pprn = pp.pprint

texts, bookmarks, snippets = parse_snippets.parse_interviews()
codes = [b for b in bookmarks if parse_snippets.is_code(b)]
#overlaps = [[lib.bkmk_to_code(b) for b in overlap] for overlap in extract_rtf.all_overlaps(bookmarks)]
overlaps = extract_rtf.all_overlaps(bookmarks)
print() or pp.pprint(snippets)

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

subject_groups_df = pd.DataFrame.from_dict({'subject': list(subject_groups.keys()), 'group': list(subject_groups.values())}).set_index('subject')

#%%############################################################################
#    Atoms Types
###############################################################################

def transpose(a2d):
    return [*zip(*a2d)]

atom_type_array = [
    ['implicit_predicate', 'C', 1],
    ['operator_precedence', 'C', 11],
    ['post_inc_dec', 'C', 13],
    ['post_inc_dec', 'NC', 14],
    ['pre_inc_dec', 'C', 19],
    ['constant_variables', 'HC', 25],
    ['constant_variables', 'HNC', 26],
    ['macro_operator_precedence', 'C', 37],
    ['pointer_arithmetic', 'HC', 45],
    ['pointer_arithmetic', 'HNC', 46],
    ['conditional_operator', 'C', 49],
    ['conditional_operator', 'NC', 50],
    ['arithmetic_as_logic', 'HC', 55],
    ['arithmetic_as_logic', 'HNC', 56],
    ['comma_operator', 'C', 61],
    ['comma_operator', 'NC', 62],
    ['preprocessor_in_statement', 'C', 71],
    ['assignment_as_value', 'C', 73],
    ['logic_as_control_flow', 'C', 79],
    ['repurposed_variable', 'C', 85],
    ['reversed_subscripts', 'C', 91],
    ['unreachable', 'HC', 99],
    ['unreachable', 'HNC', 100],
    ['change_of_literal_encoding', 'C', 105],
    ['omitted_curly_braces', 'C', 109],
    ['type_conversion', 'C', 115]]

atom_type_df = pd.DataFrame(atom_type_array, columns=['atom', 'confusingness', 'qid'])

#post-increment obfuscated rates ((0.5833333 + 0.5306122 + 0.5102041) / 3)
#pre-increment obfuscated rates ((0.6041667 + 0.7551020 + 0.5510204) / 3)

# (0.9166667 + 0.9183673 + 0.8163265) / 3
# (0.7500000 + 0.8367347 + 0.8163265) / 3

#snippet_effectsize_df[snippet_effectsize_df['qid'] & [19, 21, 23]]

snippet_effectsize_array = [
    [1,  0.32274861, 0.8958333, 1.0000000],
    [3,  0.38765744, 0.7142857, 0.8979592],
    [5,  0.00000000, 0.7346939, 0.7346939],
    [7,  0.38592249, 0.8510638, 1.0000000],
    [9,  0.37796447, 0.7551020, 0.8979592],
    [11,  0.25819889, 0.6530612, 0.7959184],
    [13,  0.54433105, 0.5833333, 0.9166667],
    [15,  0.59230570, 0.5306122, 0.9183673],
    [17,  0.49160514, 0.5102041, 0.8163265],
    [19,  0.28022427, 0.6041667, 0.7500000],
    [21,  0.16495722, 0.7551020, 0.8367347],
    [23,  0.40526180, 0.5510204, 0.8163265],
    [25,  0.14433757, 0.9791667, 1.0000000],
    [27,           0, 1.0000000, 1.0000000],
    [29,  0.08247861, 0.9795918, 0.9591837],
    [37,  0.82915620, 0.2083333, 0.8958333],
    [41,  0.11664237, 0.9183673, 0.9591837],
    [43,  0.08333333, 0.4583333, 0.4166667],
    [45,  0.35659298, 0.7346939, 0.9183673],
    [47,  0.16386838, 0.6122449, 0.5102041],
    [49,  0.47871355, 0.7708333, 1.0000000],
    [51,  0.41666667, 0.7500000, 0.9583333],
    [53,  0.49487166, 0.7551020, 1.0000000],
    [55,  0.19364917, 0.8958333, 0.9583333],
    [57,  0.08247861, 0.9591837, 0.9795918],
    [59,  0.00000000, 0.9591837, 0.9591837],
    [61,  0.66395281, 0.5000000, 0.9791667],
    [63,  0.31943828, 0.4489796, 0.6530612],
    [65,  0.00000000, 0.4897959, 0.4897959],
    [67,  0.15593624, 0.2127660, 0.2978723],
    [69,  0.71428571, 0.4897959, 1.0000000],
    [71,  0.89214257, 0.2040816, 1.0000000],
    [73,  0.59511904, 0.6458333, 1.0000000],
    [75,  0.67813269, 0.3673469, 0.8979592],
    [77,  0.52236453, 0.3265306, 0.7142857],
    [79,  0.58925565, 0.2708333, 0.6875000],
    [81,  0.90350790, 0.1224490, 0.9387755],
    [83,  0.00000000, 0.5102041, 0.5102041],
    [85,  0.28022427, 0.5208333, 0.6666667],
    [87,  0.06734350, 0.4081633, 0.3673469],
    [89,  0.45042330, 0.4897959, 0.7551020],
    [91,  0.33333333, 0.5833333, 0.7500000],
    [93,  0.47951222, 0.4081633, 0.6734694],
    [95,  0.42605779, 0.5714286, 0.8367347],
    [97,  0.08333333, 0.9375000, 0.9583333],
    [99,  0.28571429, 0.9183673, 1.0000000],
    [101,          0, 1.0000000, 1.0000000],
    [103, 0.92421138, 0.1458333, 1.0000000],
    [105, 0.79685973, 0.1428571, 0.8163265],
    [107, 0.47951222, 0.4693878, 0.7346939],
    [109, 0.16666667, 0.7083333, 0.7916667],
    [111, 0.19166297, 0.5102041, 0.6326531],
    [113, 0.38180177, 0.6326531, 0.8367347],
    [115, 0.04811252, 0.8333333, 0.8125000],
    [117, 0.31183152, 0.6734694, 0.8571429],
    [119, 0.80952381, 0.2448980, 0.9387755]]


snippet_effectsize_df = pd.DataFrame(snippet_effectsize_array, columns=['qid', 'effect-size', 'C-rate', 'NC-rate'])

snippet_old_correct_rates_df = snippet_effectsize_df[['qid', 'C-rate']].rename(columns={'C-rate':'oldrate'}).append(
        snippet_effectsize_df[['qid', 'NC-rate']].rename(columns={'NC-rate':'oldrate'}).add([1, 0]), sort=False)

#%%############################################################################
#    Parse survey data
###############################################################################

survey_df = pd.read_csv('survey/Think Aloud Survey Results - Survey.csv')
survey_df.set_index('Subject', inplace=True)


survey_langs_df = pd.read_csv('survey/Think Aloud Survey Results - Languages.csv')

survey_first_lang_df = survey_langs_df.loc[survey_langs_df.groupby('Subject')['Learned Year'].idxmin()]
survey_first_lang_df['Years Programming'] = survey_first_lang_df.apply(lambda row: 2019-row['Learned Year'], axis=1)
survey_first_lang_df.set_index('Subject', inplace=True)
survey_first_lang_df

survey_df = survey_df.join(survey_first_lang_df['Years Programming'])



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

disc_qs = [{**c, 'snippet': s.snippet} for s in snippets for c in s.discussion_codes if c['codename'] == 'Discussion Question']

disc_q_codes = []
for q in disc_qs:
    overlapping_codes = [code for code in codes if extract_rtf.overlap_bkmk(code, q) > 0]
    disc_q_codes.append({**lib.removekey(q, 'text'), 'codes': [c['codename'] for c in overlapping_codes]})

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
pd.set_option('display.max_rows', 500)
print(snippets_df[['subject', 'snippet', 'answer']])

snippets_df = snippets_df.join(subject_groups_df, on='subject')
snippets_df['group'] = snippets_df['group'].astype("category").cat.reorder_categories(['student', 'user', 'librarian'])

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

right_snippets_df = snippets_df[snippets_df['answer'] != 'Wrong']

subject_answer_sums_df = right_snippets_df.groupby('subject')['answer'].count().reset_index()

years_answers_df = subject_answer_sums_df.join(survey_first_lang_df[['Learned Year']], on='subject')

years_answers_df['years_experience'] = years_answers_df.apply(lambda row: 2019-row['Learned Year'], axis=1)

years_answers_df['subject_group'] = years_answers_df['subject'].map(subject_groups)

plt.close()
sns.set(rc={'figure.figsize':(5,5)})
years_vs_correctness_plot = sns.scatterplot(x='years_experience', y='answer', hue='subject_group', data=years_answers_df, s = 400)
years_vs_correctness_plot.set(ylim=(0,8.5),
                              xlabel="Years Programming", ylabel="Correct Answers")
plt.legend(loc='lower right')

for idx in range(0,len(years_answers_df)):
    x, y, text = years_answers_df[['years_experience', 'answer', 'subject']].iloc[idx]
    text = int(text)

    offsets = {
        4168: -.8,
        7640: .8,
        6061: -.3,
        8888: .2}

    x += offsets.get(text, 0)

    years_vs_correctness_plot.text(x, y, text, size=7, color='black', weight='semibold', horizontalalignment='center', verticalalignment='center')

plt.savefig('img/years_vs_correctness.pdf')

#%%############################################################################
#    All unique codes
###############################################################################

from collections import Counter

pprn(Counter([c['codename'] for c in codes]))

#%%############################################################################
#    Causes of Confusion
###############################################################################


causes_confusion = [c for c in codes if c['codename'] == 'Causes of Confusion']

pprn(causes_confusion)

non_student_wrong_answers = [s for s in snippets if s.answer == 'Wrong' and subject_groups[s.subject] != 'student']

pprn(non_student_wrong_answers)

# The only wrong answer from a librarian was on snippet #115 (users got wrong 61 and 79)
# Find corresponding wrongs among students
matching_student_wrong_answers = [s for s in snippets if s.answer == 'Wrong' and subject_groups[s.subject] == 'student' and s.snippet in [115, 61, 79]]

pprn(matching_student_wrong_answers)

wrong_snippets = [s for s in snippets if s.answer == 'Wrong']

pprn(wrong_snippets)

#%%############################################################################
#    Which questions were most confusing
###############################################################################

snippet_answer_groups = snippets_df.groupby(['snippet', 'answer'], as_index=False).size().to_frame('size').reset_index()
snippet_answer_sums = snippet_answer_groups.groupby(['snippet', 'answer']).agg({'size': 'sum'})
snippet_answer_rates = snippet_answer_sums.groupby(level=0).apply(lambda x: x / float(x.sum())).rename(columns={'size': 'rate'})

snippet_answer_rates.reset_index(inplace=True)
snippet_correct_rates = snippet_answer_rates[snippet_answer_rates['answer'] == 'Right']
snippet_correct_rates = snippet_correct_rates.join(atom_type_df.set_index('qid'), on='snippet').join(snippet_old_correct_rates_df.set_index('qid'), on='snippet')
snippet_correct_rates['oldrate_jitter'] = snippet_correct_rates['oldrate'] + (0.01 * snippet_correct_rates.index.map(lambda x: x % 10) * snippet_correct_rates['rate'].map(lambda x: 1 if x == 1 else 0))
#snippet_correct_rates.sort_values(by='rate')

plt.close()
snippet_correctness_plot = sns.scatterplot(x='oldrate_jitter', y='rate', hue='confusingness', data=snippet_correct_rates, s = 70, x_jitter=.2)
snippet_correctness_plot.set(ylim=[0,1.03], xlim=[0,1.1], xlabel="Previous Correctness", ylabel="Current Correctness")

for idx in range(0,len(snippet_correct_rates)):
    x, y, text = snippet_correct_rates[['oldrate_jitter', 'rate', 'atom']].iloc[idx]
    snippet_correctness_plot.text(x+0.008*len(text)**0.8, y-0.008*len(text)**0.8, text, size=5, color='black', weight='semibold', rotation=315, horizontalalignment='center', verticalalignment='center')

plt.legend(loc='lower right')
plt.savefig('img/snippet_correctness.pdf')

#%%############################################################################
#    Operator Precedence - Right for wrong reason
###############################################################################

right_wrong_reason = [{'snippet': s, 'code': c} for s in snippets for c in s.codes + s.discussion_codes if c['codename'] == 'Correct for Wrong Reasons']

op_prec_right_wrong_reason = [d for d in right_wrong_reason if d['snippet'].snippet == 11]

pprn(op_prec_right_wrong_reason)



#%%############################################################################
#    Find every "caught own mistake", ignoring "before" or "after"
###############################################################################

def text_context(subject, n_context, start, end):
    return texts[subject][start-n_context:start] + \
           "\nvvvvvvvvvvv\n" + \
           texts[subject][start:end] + \
           "\n^^^^^^^^^^^\n" + \
           texts[subject][end:end+n_context]

def find_snippets_by_codes(snippets, code_names):
    return [{'snippet': s, 'code': c} for s in snippets for c in
            [{**x, 'section': 'Evaluation'} for x in s.codes] +
            [{**x, 'section': 'Discussion'} for x in s.discussion_codes
            ] if c['codename'] in code_names]

def print_code_snippets(code_snippets, context=200):
    for sc in code_snippets:
        s = sc['snippet']
        c = sc['code']
        print("\n\n-----------------")
        print(s.subject, s.snippet, c['section'], s.answer, subject_groups[s.subject])
        print("-----------------")
        print(text_context(s.subject, context, c['start'], c['end']))

caught_own_mistakes = find_snippets_by_codes(snippets, ['Caught Own Mistake Before Prompted', 'Caught Own Mistake After Prompted'])

print_code_snippets(caught_own_mistakes)


#%%############################################################################
#    Participants table
###############################################################################

#pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
print(survey_df[['Age', 'Preferred Language', 'Proficiency C/C++', 'Years Programming']].join(subject_groups_df).to_csv())

#%%############################################################################
#    Find every "correct for wrong reason"
###############################################################################

correct_for_wrong_reasons = find_snippets_by_codes(snippets, ['Correct for Wrong Reasons'])

print_code_snippets(correct_for_wrong_reasons)

#%%############################################################################
#    Code rates for different experience groups
###############################################################################

codes_df = pd.DataFrame([{**c, 'snippet': s.snippet, 'atom': s.atom,
               'answer': s.answer, 'confidence': s.confidence} for s in snippets for c in
              [{**x, 'section': 'Evaluation'} for x in s.codes] +
              [{**x, 'section': 'Discussion'} for x in s.discussion_codes]])

codes_df = codes_df.join(subject_groups_df, on='subject')
codes_df.rename(columns={'codename': 'code', 'group': 'subject_group'}, inplace=True)

print(codes_df.groupby(['subject_group', 'code']).size().sort_values(ascending=False).to_csv())

codes_students_df = codes_df[codes_df['subject_group']=='student']
codes_professionals_df = codes_df[codes_df['subject_group']!='student']


codes_students_df.groupby(['code']).size().sort_values(ascending=False)
print(codes_professionals_df.groupby(['code']).size().sort_values(ascending=False).to_csv())


paranoia = find_snippets_by_codes(snippets, ['Paranoia'])

len(paranoia)

print_code_snippets(paranoia)

judgement = find_snippets_by_codes(snippets, ['Snippet Value Judgement', 'Would Have Written it Differently', 'Code Review'])

print_code_snippets(judgement)

judgement_counts = collections.Counter([x['snippet'].subject for x in judgement])

set(subject_groups.keys()) - set(judgement_counts.keys())

judgement_counts_df = pd.DataFrame.from_dict(judgement_counts, columns=['n_judgements'], orient='index')
judgement_counts_df.index.name = 'subject'

judgement_years_df = judgement_counts_df.join(years_answers_df[['subject', 'answer', 'years_experience', 'subject_group']].set_index('subject'))
judgement_years_df

mpl.cm.get_cmap('viridis')
judgement_years_df['subject_group_cvals'] = judgement_years_df['subject_group'].map(lambda sg: {'student': 0, 'user': 127, 'librarian': 255}[sg])

mkr_dict = {'student': 'o', 'user': '1', 'librarian': 's'}
judgement_years_df['subject_group_markers'] = judgement_years_df['subject_group'].map(lambda sg: mkr_dict[sg])

plt.close()
#judgement_vs_years_plot = judgement_years_df.plot.scatter(x='years_experience', y='n_judgements', c='answer', colormap='plasma_r', s=100)
#judgement_vs_years_plot = judgement_years_df.plot.scatter(x='years_experience', y='n_judgements', c='subject_group_cvals', colormap='plasma_r', s=100)
#judgement_years_df.plot.scatter(x='answer', y='n_judgements')

for kind in mkr_dict:
    d = judgement_years_df[judgement_years_df['subject_group']==kind]
    judgement_vs_years_plot = plt.scatter(d['years_experience'], d['n_judgements'],
                s = 100,
                c = mpl.cm.get_cmap('plasma_r')(50*(d['answer']-3)),
                marker = mkr_dict[kind])
plt.xlabel("Years Experience")
plt.ylabel("Judgy Comments")
plt.show()



judgement_years_df.corr()
judgement_years_df
model = ols('n_judgements ~ years_experience + answer', data=judgement_years_df).fit()
predictions = model.predict(judgement_years_df) # make the predictions by the model

judgement_prediction_df = judgement_counts_df.join(pd.DataFrame(predictions, columns=['predicted']))

judgement_prediction_plot = judgement_prediction_df.plot.scatter(y='n_judgements', x='predicted')
judgement_prediction_plot.set(ylim=[0,14], xlim=[0,14], ylabel="Judgy Comments", xlabel="~ Years Experience + Answer Correctness")
judgement_prediction_plot.plot([-1, 15], [-1, 15], marker = 'o')
plt.savefig('img/judgement_prediction.pdf')

judgement_prediction_df.corr()

# Print out the statistics
model.summary()

sm.graphics.plot_partregress_grid(model)

#%%############################################################################
#    Confidence vs Correctness by Atom
###############################################################################
nc_snippets_df = snippets_df[snippets_df['confusingness'] != 'Atom']
c_snippets_df = atom_snippets_df = snippets_df[snippets_df['confusingness'] == 'Atom']
snippet_confidence_df = pd.DataFrame(atom_snippets_df)
snippet_confidence_df['snippet_cat'] = snippet_confidence_df['snippet'].map(str)
snippet_confidence_df['answer_size'] = snippet_confidence_df['answer'].map(lambda x: 50 if x == 'Right' else 120)

conf_colors = {'Wrong': mpl.cm.get_cmap('plasma')(20), 'Right': mpl.cm.get_cmap('plasma')(120)}

snippet_confidence_df['answer_color'] = snippet_confidence_df['answer'].map(lambda x: conf_colors[x])
snippet_confidence_df
#confidence_correctness_plot = sns.scatterplot(x='snippet', y='confidence', hue='answer', data=snippet_confidence_df, s = 'answer_size', x_jitter=.2)

c_snippets_df.groupby(['answer', 'confidence']).size()
nc_snippets_df.groupby(['answer', 'confidence']).size()
# finding: all NC snippets were full-confidence and correct


plt.close()
for kind in ('Wrong', 'Right'):
    d = snippet_confidence_df[snippet_confidence_df['answer']==kind]
    confidence_correctness_plot = plt.scatter(d['snippet_cat'], d['confidence'],
                s = d['answer_size'],
                c = d['answer_color'])
plt.show()

snippets_df[snippets_df['answer']=='Wrong'].groupby(['snippet', 'confidence']).size()
snippets_df[snippets_df['answer']=='Right'].groupby(['snippet', 'confidence']).size()

snippets_df.groupby(['answer', 'confidence']).size()

right_snippets_df = snippets_df[snippets_df['answer']!='Wrong']
wrong_snippets_df = snippets_df[snippets_df['answer']=='Wrong']
wrong_snippets_df['group']
wrong_snippets_df[['snippet', 'group', 'confidence']].sort_values('snippet')
# finding: every professional error had confidence 5
# finding: 3/4 of answers to #79 were wrong

plt.close()
right_wrong_conf_fig, axs = plt.subplots(ncols=2, figsize=(6,3))
right_wrong_conf_fig.subplots_adjust(top=0.8, bottom=0.2)
right_conf_plot = sns.countplot(x='confidence', hue='group', data=right_snippets_df, ax=axs[0], order=[1,2,3,4,5,6], hue_order=['student', 'user', 'librarian'])
right_conf_plot.set(ylim=(0,29))
right_conf_plot.set_title('Correct Answers')
right_conf_plot.legend(loc='upper left')
wrong_conf_plot = sns.countplot(x='confidence', hue='group', data=wrong_snippets_df, ax=axs[1], order=[1,2,3,4,5,6], hue_order=['student', 'user', 'librarian'])
wrong_conf_plot.set(ylim=(0,29))
wrong_conf_plot.set_title('Incorrect Answers')
wrong_conf_plot.set_ylabel('')
wrong_conf_plot.legend_.remove()
right_wrong_conf_fig.suptitle('Confidence of Answers', fontsize=16)

# draw group separator grid
for i in range(6):
    right_conf_plot.axvline(i+0.5, ymax=1, color="white")
    wrong_conf_plot.axvline(i+0.5, ymax=1, color="white")

plt.show()
plt.savefig('img/right_wrong_conf.pdf')

snippets_df.groupby(['group', 'confidence']).size()

#%%############################################################################
#    Correctness vs confidence by snippet
###############################################################################


confidence_correctness_agg_df = snippet_confidence_df.groupby(['snippet']).agg({'confidence':'mean', 'answer':lambda x: x.value_counts()['Right']/len(x)})

plt.close()
confidence_correctness_agg_plot = sns.scatterplot(x='confidence', y='answer', data=confidence_correctness_agg_df)
plt.show()

snippets_df[snippets_df['snippet']==79]







#%%############################################################################
#    Confidence vs Experience
###############################################################################

experience_confidence_df = atom_snippets_df[['subject', 'atom', 'confusingness', 'answer', 'confidence']].join(survey_df[['Years Programming']], on='subject')

#cmap = sns.cubehelix_palette(as_cmap=True, dark=0, light=1, reverse=True)
#experience_confidence_plot = sns.kdeplot(experience_confidence_df['Years Programming'], experience_confidence_df['confidence'], cmap=cmap, n_levels=60, shade=True)
#with sns.axes_style("white"):
#    experience_confidence_plot = sns.jointplot(experience_confidence_df['Years Programming'], experience_confidence_df['confidence'], kind='hex')
#plt.hist2d(experience_confidence_df['Years Programming'], experience_confidence_df['confidence'], bins=(6,5), cmap=plt.cm.jet)
plt.close()
#experience_confidence_plot = sns.scatterplot(x='Years Programming', y='confidence', hue='answer', s=70, data=experience_confidence_df)
plt.show()

snippets_df[snippets_df['confusingness'] == 'Transformation'].groupby('confidence').size()

#%%############################################################################
#    Dispersion vs confidence
###############################################################################

dispersion_2016_df = pd.read_csv('snippet-study-dispersion.csv').set_index('snippet')

snippet_dispersion_df = atom_snippets_df.join(dispersion_2016_df, on='snippet')


plt.close()
snippet_dispersion_plot = sns.scatterplot(x='entropy', y='confidence', hue='answer', s=70, data=snippet_dispersion_df)
sns.scatterplot(x='entropy', y='confidence', s=120, data=snippet_dispersion_df[snippet_dispersion_df['answer']=='Wrong'])
plt.show()

plt.hist2d(x='entropy', y='confidence', data=snippet_dispersion_df, bins=(6,5), cmap=plt.cm.jet)
snippet_dispersion_df[['entropy', 'answer', 'confidence']]
judgement_prediction_df.corr()


snippet_dispersion_df['high_entropy'] = snippet_dispersion_df['entropy'].map(lambda x: x >= 1)

wrong_snippet_dispersion_df = snippet_dispersion_df[snippet_dispersion_df['answer']=='Wrong']

wrong_snippet_dispersion_df[['confidence', 'high_entropy']].groupby('high_entropy').agg('mean')

scipy.stats.ttest_ind(wrong_snippet_dispersion_df[wrong_snippet_dispersion_df['high_entropy']==True]['confidence'], wrong_snippet_dispersion_df[wrong_snippet_dispersion_df['high_entropy']==False]['confidence'])

wrong_snippet_dispersion_df['snippet_str'] = pd.Categorical(wrong_snippet_dispersion_df['snippet'].map(lambda s: 'q'+str(int(s))))

plt.close()
wrong_snippet_dispersion_plot = sns.scatterplot(x='entropy', y='confidence', hue='snippet_str', s=70, data=wrong_snippet_dispersion_df)
wrong_snippet_dispersion_plot.legend_.remove()
for idx in range(0,len(wrong_snippet_dispersion_df)):
    x, y, text = wrong_snippet_dispersion_df[['entropy', 'confidence', 'snippet_str']].iloc[idx]
    wrong_snippet_dispersion_plot.text(x+.05, y+.2, text, size=5, color='black', weight='semibold', horizontalalignment='center', verticalalignment='center')
plt.show()


#%%############################################################################
#    Correctness vs confidence examples
###############################################################################

codes_df = pd.DataFrame([{'subject': s.subject, 'snippet': s.snippet, **c} for s in snippets for c in s.codes])

snippet_codes_df = snippets_df.set_index(['subject', 'snippet']).join(codes_df.set_index(['subject', 'snippet']), how='right', lsuffix='_snippet')
snippet_codes_df

snippet_codes_df.groupby(['confidence','answer','codename']).size()
