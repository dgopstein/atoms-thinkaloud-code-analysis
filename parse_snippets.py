import extract_rtf
import pprint
import itertools
import re
#from frozendict import frozendict
import glob
from intervaltree import Interval, IntervalTree

class Snippet:
    SNIPPET_PAT = 'Snippet - (.*)'
    ANSWER_PAT = 'Answer - (.*)'
    CONFUSINGNESS_PAT = 'Confusingness - (.*)'
    CONFIDENCE_PAT = 'Confidence - (.*)'
    ATOM_PAT = '(.*[^-]) (Atom|Transformation)'
    SECTION_PAT = 'Section - (.*)'

    def find_content(regex, overlap):
        element = next(x for x in overlap if re.match(regex, x['content']))
        match = re.match(regex, element['content'])
        return {'start': element['start'], 'end': element['end'], 'match': match.group(1)}

    def create(subject, overlap):
        try:
            return Snippet(subject, overlap)
        except StopIteration: # this overlap doesn't descript a snippet (maybe it's a code inside a snippet)
            return None

    def __init__(self, subject, overlap):
        snippet = Snippet.find_content(self.SNIPPET_PAT, overlap)
        self.subject = subject
        self.start = snippet['start']
        self.end = snippet['end']
        self.snippet = int(snippet['match'])
        self.answer = Snippet.find_content(self.ANSWER_PAT, overlap)['match']
        self.confusingness = Snippet.find_content(self.CONFUSINGNESS_PAT, overlap)['match']
        self.confidence = int(Snippet.find_content(self.CONFIDENCE_PAT, overlap)['match'])
        self.atom = Snippet.find_content(self.ATOM_PAT, overlap)['match']
        self.section = Snippet.find_content(self.SECTION_PAT, overlap)['match']
        self.codes = []

    def __repr__(self):
       return '%s <%d, %d> (%d - %s %s) [%s - %d]' % (self.subject, self.start, self.end, self.snippet, self.atom, self.confusingness, self.answer, self.confidence)

    def __hash__(self):
       return (self.subject, self.start, self.end, self.snippet, self.atom, self.confusingness, self.answer, self.confidence).__hash__()

    def __eq__(self, other):
       return (self.subject, self.start, self.end, self.snippet, self.atom, self.confusingness, self.answer, self.confidence) == (other.subject, other.start, other.end, other.snippet, other.atom, other.confusingness, other.answer, other.confidence)

    def __lt__(self, other):
       return self.start < other.start

def parse_interviews():
    interviews_glob = '/Users/dgopstein/nyu/confusion/think-aloud/qda_miner/*interview.RTF'

    all_snippets = []
    all_bookmarks = []
    all_text = {}

    inpath = '/Users/dgopstein/nyu/confusion/think-aloud/qda_miner/4281 interview.RTF'
    for inpath in glob.glob(interviews_glob):
        #print('inpath', inpath)

        subject = int(re.match('.*(\d{4})[-_ ]interview.RTF', inpath).group(1))

        with open(inpath, 'r', encoding='latin1') as infile:
            doc = infile.read()

        bookmarks, stripped_rtf = extract_rtf.striprtf(doc)

        for b in bookmarks:
            b['subject'] = subject

        all_bookmarks.extend(bookmarks)
        all_text[subject] = stripped_rtf

        overlaps = extract_rtf.all_overlaps(bookmarks)
        snippet_list = [Snippet.create(subject, ol) for ol in overlaps if Snippet.create(subject, ol) if not None]
        snippets = set(snippet_list)

        add_codes_to_snippets(snippets, bookmarks, stripped_rtf)

        all_snippets.extend(sorted(snippets))

    return (all_text, all_bookmarks, all_snippets)

# filter out the bookmarks that describe snippets and sections
def is_code(b):
    return not re.match('|'.join([Snippet.SNIPPET_PAT, Snippet.ANSWER_PAT, Snippet.CONFUSINGNESS_PAT, Snippet.CONFIDENCE_PAT, Snippet.ATOM_PAT, Snippet.SECTION_PAT]), b['content'])

def add_codes_to_snippets(snippets, bookmarks, text):
    snippet_intervals = [Interval(s.start, s.end, s) for s in snippets]
    snippet_tree = IntervalTree(snippet_intervals)

    for b in bookmarks:
        if is_code(b):
            snippet_set = snippet_tree[b['start']:b['end']]
            if len(snippet_set) == 1: # there are many codes after the evaluation section
                snippet_interval = next(iter(snippet_set))
                b['text'] = text[b['start']:b['end']]
                snippet_interval.data.codes.append(b)

#pp.pprint(overlaps[1])
#texts, bookmarks, snippets = parse_interviews()
#print() or pp.pprint(parse_interviews())
