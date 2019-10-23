#! /usr/bin/env python3

import sys, re
from pyth.plugins.rtf15.reader import Rtf15Reader

inpath = '/Users/dgopstein/nyu/confusion/think-aloud/qda_miner/4168 interview.RTF'
#inpath = sys.argv[1]

#with open(inpath, 'rb') as infile:
with open(inpath, 'r', encoding='latin1') as infile:
    text = infile.read()

matches = re.findall('{\\\\\*\\\\bkmkstart ([^:]+):[^}]*}(.*?){\\\\\*\\\\bkmkend \\1:[^:]*}', text)

for (tag, string) in matches:
    print(tag, string)

