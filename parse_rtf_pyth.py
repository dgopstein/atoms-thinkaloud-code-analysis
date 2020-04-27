#! /usr/bin/env python3

import sys
#import extract_rtf
from pyth.plugins.rtf15.reader import Rtf15Reader

inpath = '/Users/dgopstein/nyu/confusion/think-aloud/qda_miner/4168 interview.RTF'
#inpath = sys.argv[1]

with open(inpath, 'rb') as infile:
    doc = Rtf15Reader.read(infile)

cs = [doc]
for c in cs:
    #[print("~all_content" c) for kid in c.content if isinstance(kid, str)]
    cs.extend(c.content)

#    if not isinstance(c, str):
#        cs.extend(c.content)
#        print(c.properties, end=' ')
#    else:
#        print('.', end=' ')
