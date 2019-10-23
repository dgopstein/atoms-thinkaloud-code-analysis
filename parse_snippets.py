import extract_rtf
import pprint
import itertools
#from frozendict import frozendict
import glob

class Snippet:
    def find_content(regex, overlap):
        element = next(x for x in overlap if re.match(regex, x['content']))
        match = re.match(regex, element['content'])
        return {'start': element['start'], 'end': element['end'], 'match': match.group(1)}

    def create(subject, overlap):
        try:
            return Snippet(subject, overlap)
        except:
            return None

    def __init__(self, subject, overlap):
        snippet = Snippet.find_content('Snippet - (.*)', overlap)
        self.subject = subject
        self.start = snippet['start']
        self.end = snippet['end']
        self.snippet = int(snippet['match'])
        self.answer = Snippet.find_content('Answer - (.*)', overlap)['match']
        self.confusingness = Snippet.find_content('Confusingness - (.*)', overlap)['match']
        self.confidence = int(Snippet.find_content('Confidence - (.*)', overlap)['match'])
        self.atom = Snippet.find_content('(.*[^-]) (Atom|Transformation)', overlap)['match']

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

    inpath = '/Users/dgopstein/nyu/confusion/think-aloud/qda_miner/4281 interview.RTF'
    for inpath in glob.glob(interviews_glob):
        #print('inpath', inpath)

        subject = int(re.match('.*(\d{4})[-_ ]interview.RTF', inpath).group(1))

        with open(inpath, 'r', encoding='latin1') as infile:
            doc = infile.read()

        bookmarks, stripped_rtf = striprtf(doc)

        overlaps = all_overlaps(bookmarks)
        snippets = set(Snippet.create(subject, x) for x in overlaps if Snippet.create(subject, x) is not None)

        all_snippets.extend(sorted(snippets))

    return all_snippets

#pp.pprint(overlaps[1])
#snippets = parse_interviews()
#print() or pp.pprint(parse_interviews())

