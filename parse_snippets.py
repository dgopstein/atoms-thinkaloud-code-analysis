import lib
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
        element = next(x for x in overlap if re.match(regex, x['codename']))
        match = re.match(regex, element['codename'])
        return {'start': element['start'], 'end': element['end'], 'match': match.group(1)}

    def create(subject, overlap):
        try:
            return EvalSnippet(subject, overlap)
        except StopIteration: # this overlap doesn't descript a snippet (maybe it's a code inside a snippet)
            try:
                return DiscussionSnippet(subject, overlap)
            except StopIteration:
                return None
            return None

    def __init__(self, subject, overlap):
        snippet = Snippet.find_content(self.SNIPPET_PAT, overlap)
        self.subject = subject
        self.start = snippet['start']
        self.end = snippet['end']
        self.snippet = int(snippet['match'])
        self.section = Snippet.find_content(self.SECTION_PAT, overlap)['match']
        self.codes = []

    def __hash__(self):
       return (self.subject, self.start, self.end, self.snippet, self.section).__hash__()

    def __eq__(self, other):
       return (self.subject, self.start, self.end, self.snippet, self.section) == (other.subject, other.start, other.end, other.snippet, other.section)

    def __lt__(self, other):
       return self.start < other.start

class DiscussionSnippet(Snippet):
    def __init__(self, subject, overlap):
        Snippet.__init__(self, subject, overlap)
        if self.section != 'Discussion':
            raise StopIteration

    def __repr__(self):
       return '%s <%d, %d> (%d - %s)' % (self.subject, self.start, self.end, self.snippet, self.section)

class EvalSnippet(Snippet):
    def __init__(self, subject, overlap):
        Snippet.__init__(self, subject, overlap)
        self.answer = Snippet.find_content(self.ANSWER_PAT, overlap)['match']
        self.confusingness = Snippet.find_content(self.CONFUSINGNESS_PAT, overlap)['match']
        self.confidence = int(Snippet.find_content(self.CONFIDENCE_PAT, overlap)['match'])
        self.atom = Snippet.find_content(self.ATOM_PAT, overlap)['match']
        self.discussion_codes = []

    def __repr__(self):
       return '%s <%d, %d> (%d - %s %s) [%s - %d]' % (self.subject, self.start, self.end, self.snippet, self.atom, self.confusingness, self.answer, self.confidence)
   
    def to_dict(self):
        return {'subject': self.subject, 'start': self.start, 'end': self.end, 'snippet': self.snippet, 'atom': self.atom, 
                'confusingness': self.confusingness, 'answer': self.answer, 'confidence': self.confidence, 'section': self.section}


def parse_interviews():
    interviews_glob = 'transcripts/*interview.RTF'

    all_snippets = []
    all_bookmarks = []
    all_text = {}

    #inpath = '/Users/dgopstein/nyu/confusion/think-aloud/qda_miner/4281 interview.RTF'
    glob.glob(interviews_glob)
    glob.glob('transcripts/*')
    glob.glob('*')
    for inpath in glob.glob(interviews_glob):
        subject = int(re.match('.*(\d{4})[-_ ]interview.RTF', inpath).group(1))

        print("subject", subject)

        with open(inpath, 'r', encoding='latin1') as infile:
            doc = infile.read()

        bookmarks, stripped_rtf = extract_rtf.striprtf(doc)

        bookmarks = [lib.bkmk_to_code(b) for b in bookmarks]
        for b in bookmarks:
            b['subject'] = subject

        all_bookmarks.extend(bookmarks)
        all_text[subject] = stripped_rtf

        overlaps = extract_rtf.all_overlaps(bookmarks)
        snippet_list = [Snippet.create(subject, ol) for ol in overlaps if Snippet.create(subject, ol) if not None]
        #eval_snippet_list = [s in snippet_list if s.section = 'Evaluation']
        #disc_snippet_list = [s in snippet_list if s.section = 'Discussion']
        combined_snippets = set(snippet_list)

        add_codes_to_snippets(combined_snippets, bookmarks, stripped_rtf)

        snippets = merge_eval_and_discussion(combined_snippets)

        all_snippets.extend(sorted(snippets))

    return (all_text, all_bookmarks, all_snippets)

# filter out the bookmarks that describe snippets and sections
def is_code(b):
    return not re.match('|'.join([Snippet.SNIPPET_PAT, Snippet.ANSWER_PAT, Snippet.CONFUSINGNESS_PAT, Snippet.CONFIDENCE_PAT, Snippet.ATOM_PAT, Snippet.SECTION_PAT]), b['codename'])

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

def merge_eval_and_discussion(combined_snippets):
    evals = [es for es in combined_snippets if es.section == 'Evaluation']
    discs = [ds for ds in combined_snippets if ds.section == 'Discussion']

    def snippet_key(s):
        return str(s.subject)+'_'+str(s.snippet)

    eval_dict = { snippet_key(es) : es for es in evals }

    for ds in discs:
        eval_dict[snippet_key(ds)].discussion_codes.extend(ds.codes)

    return sorted(eval_dict.values())

#pp.pprint(overlaps[1])
#texts, bookmarks, snippets = parse_interviews()
#print() or pp.pprint(parse_interviews())
