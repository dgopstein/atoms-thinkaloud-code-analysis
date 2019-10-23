# -*- coding: utf-8 -*-

"""
Extract text in RTF Files. Refactored to use with Python 3.x
Source:
    http://stackoverflow.com/a/188877

Code created by Markus Jarderot: http://mizardx.blogspot.com
"""

import re

#inpath = '/Users/dgopstein/nyu/confusion/think-aloud/qda_miner/4168 interview.RTF'
#
#with open(inpath, 'r', encoding='latin1') as infile:
#    doc = infile.read()

##################################
#bookmarks, stripped_rtf = striprtf(doc[:14000])
#print('stripped', stripped_rtf)
#print()
#for x in bookmarks:
#   print('bookmarks', x)
#for overlap in all_overlaps(bookmarks):
#   print('overlap')
#   for x in overlap:
#      print('  ', x)
##################################

# Find every grouping of overlapped bookmarks
def all_overlaps(unsorted_bookmarks):
   starts = sorted(unsorted_bookmarks, key=lambda x: x['start'])
   ends = sorted(unsorted_bookmarks, key=lambda x: x['end'])

   dummy = {'start': ends[-1]['end'] + 1, 'end': ends[-1]['end'] + 2}

   stack = []

   overlaps = []
   while starts or ends:
      next_end = ends[0]
      next_start = starts[0] if starts else dummy
      if next_end['start'] < next_start['start']:
         stack.remove(next_end)
         ends.remove(next_end)
      else:
         stack.append(next_start)
         starts.remove(next_start)
         #if len(stack) > 1:
         overlaps.append(stack.copy())

   def bookmark_to_tuple(b):
      return (b['start'], b['end'], b['content'])

   def tuple_to_bookmark(t):
      return {'start': t[0], 'end': t[1], 'content': t[2]}

   def set_diff(a, b):
      a_set = set(bookmark_to_tuple(x) for x in a)
      b_set = set(bookmark_to_tuple(x) for x in b)
      return [tuple_to_bookmark(x) for x in a_set.difference(b_set)]

   # remove redundant overlaps created by several codes spanning
   # the same section appearing to be created in sequence
   #distinct_overlaps = [overlaps.pop(0)]
   #for overlap in overlaps:
   #   prev_overlap = distinct_overlaps[-1]
   #   diff = set_diff(overlap, prev_overlap)
   #   print('prev_overlap', prev_overlap)
   #   print('overlap', overlap)
   #   new_element = diff[0]
   #   if any(new_element['start'] == e['start'] and
   #           new_element['end'] == e['end']
   #           for e in overlap):
   #       distinct_overlaps.pop()

   #   distinct_overlaps.append(overlap)

   return overlaps

def overlap(a, b):
   return min(a[1], b[1]) - max(a[0], b[0])

def in_bookmark(idx_stack):
   return len(idx_stack) > 0 and idx_stack[-1]['word'] == 'bkmkstart'

# keep track of number of plain-text characters in output for indexing
def out_append(out_count, out, s):
  out.append(s)
  out_count += len(s)
  return out_count

def striprtf(text):
   pattern = re.compile(r"\\([a-z]{1,32})(-?\d{1,10})?[ ]?|\\'([0-9a-f]{2})|\\([^a-z])|([{}])|[\r\n]+|(.)", re.I)
   # control words which specify a "destionation".
   destinations = frozenset((
      'aftncn','aftnsep','aftnsepc','annotation','atnauthor','atndate','atnicn','atnid',
      'atnparent','atnref','atntime','atrfend','atrfstart','author','background',
      'blipuid','buptim','category','colorschememapping',
      'colortbl','comment','company','creatim','datafield','datastore','defchp','defpap',
      'do','doccomm','docvar','dptxbxtext','ebcend','ebcstart','factoidname','falt',
      'fchars','ffdeftext','ffentrymcr','ffexitmcr','ffformat','ffhelptext','ffl',
      'ffname','ffstattext','field','file','filetbl','fldinst','fldrslt','fldtype',
      'fname','fontemb','fontfile','fonttbl','footer','footerf','footerl','footerr',
      'footnote','formfield','ftncn','ftnsep','ftnsepc','g','generator','gridtbl',
      'header','headerf','headerl','headerr','hl','hlfr','hlinkbase','hlloc','hlsrc',
      'hsv','htmltag','info','keycode','keywords','latentstyles','lchars','levelnumbers',
      'leveltext','lfolevel','linkval','list','listlevel','listname','listoverride',
      'listoverridetable','listpicture','liststylename','listtable','listtext',
      'lsdlockedexcept','macc','maccPr','mailmerge','maln','malnScr','manager','margPr',
      'mbar','mbarPr','mbaseJc','mbegChr','mborderBox','mborderBoxPr','mbox','mboxPr',
      'mchr','mcount','mctrlPr','md','mdeg','mdegHide','mden','mdiff','mdPr','me',
      'mendChr','meqArr','meqArrPr','mf','mfName','mfPr','mfunc','mfuncPr','mgroupChr',
      'mgroupChrPr','mgrow','mhideBot','mhideLeft','mhideRight','mhideTop','mhtmltag',
      'mlim','mlimloc','mlimlow','mlimlowPr','mlimupp','mlimuppPr','mm','mmaddfieldname',
      'mmath','mmathPict','mmathPr','mmaxdist','mmc','mmcJc','mmconnectstr',
      'mmconnectstrdata','mmcPr','mmcs','mmdatasource','mmheadersource','mmmailsubject',
      'mmodso','mmodsofilter','mmodsofldmpdata','mmodsomappedname','mmodsoname',
      'mmodsorecipdata','mmodsosort','mmodsosrc','mmodsotable','mmodsoudl',
      'mmodsoudldata','mmodsouniquetag','mmPr','mmquery','mmr','mnary','mnaryPr',
      'mnoBreak','mnum','mobjDist','moMath','moMathPara','moMathParaPr','mopEmu',
      'mphant','mphantPr','mplcHide','mpos','mr','mrad','mradPr','mrPr','msepChr',
      'mshow','mshp','msPre','msPrePr','msSub','msSubPr','msSubSup','msSubSupPr','msSup',
      'msSupPr','mstrikeBLTR','mstrikeH','mstrikeTLBR','mstrikeV','msub','msubHide',
      'msup','msupHide','mtransp','mtype','mvertJc','mvfmf','mvfml','mvtof','mvtol',
      'mzeroAsc','mzeroDesc','mzeroWid','nesttableprops','nextfile','nonesttables',
      'objalias','objclass','objdata','object','objname','objsect','objtime','oldcprops',
      'oldpprops','oldsprops','oldtprops','oleclsid','operator','panose','password',
      'passwordhash','pgp','pgptbl','picprop','pict','pn','pnseclvl','pntext','pntxta',
      'pntxtb','printim','private','propname','protend','protstart','protusertbl','pxe',
      'result','revtbl','revtim','rsidtbl','rxe','shp','shpgrp','shpinst',
      'shppict','shprslt','shptxt','sn','sp','staticval','stylesheet','subject','sv',
      'svb','tc','template','themedata','title','txe','ud','upr','userprops',
      'wgrffmtfilter','windowcaption','writereservation','writereservhash','xe','xform',
      'xmlattrname','xmlattrvalue','xmlclose','xmlname','xmlnstbl',
      'xmlopen',
   ))
   # Translation of some special characters.
   specialchars = {
      'par': '\n',
      'sect': '\n\n',
      'page': '\n\n',
      'line': '\n',
      'tab': '\t',
      'emdash': '\u2014',
      'endash': '\u2013',
      'emspace': '\u2003',
      'enspace': '\u2002',
      'qmspace': '\u2005',
      'bullet': '\u2022',
      'lquote': '\u2018',
      'rquote': '\u2019',
      'ldblquote': '\201C',
      'rdblquote': '\u201D',
   }
   idx_stack = [] # keep track of positions in the file
   bookmarks = [] # list of bookmarks (after they've ended)
   parsing_bkmkstart = False
   parsing_bkmkend = False
   current_bkmkend = []
   out_count = 0

   stack = []

   ignorable = False       # Whether this group (and all inside it) are "ignorable".
   ucskip = 1              # Number of ASCII characters to skip after a unicode character.
   curskip = 0             # Number of ASCII characters left to skip
   out = []                # Output buffer.
   for match in pattern.finditer(text):
      word,arg,hex,char,brace,tchar = match.groups()
      if brace:
         curskip = 0
         if brace == '{':
            # Push state
            stack.append((ucskip,ignorable))
         elif brace == '}':
            parsing_bkmkstart = False
            parsing_bkmkend = False

            # A bookmark is being terminated, figure out which one, and transfer it from the list of open bookmarks to the list of closed bookmarks, changing it's name to be more human readable in the process
            if current_bkmkend:
                matching_starts = [bkmk for bkmk in idx_stack if bkmk['content'] == current_bkmkend]

                assert len(matching_starts) == 1
                matching_start = matching_starts[0]
                matching_start['end'] = out_count
                matching_start['content'] = re.sub('(^[^:]*):.*', r'\1', ''.join(matching_start['content']))
                idx_stack.remove(matching_start)
                bookmarks.append(matching_start)
                current_bkmkend = []
            # Pop state
            ucskip,ignorable = stack.pop()
      elif char: # \x (not a letter)
         curskip = 0
         if char == '~':
            if not ignorable:
                out_count = out_append(out_count, out, '\xA0')
         elif char in '{}\\':
            if not ignorable:
               out_count = out_append(out_count, out, char)
         #elif char == '*':
         #   ignorable = True
      elif word: # \foo
         curskip = 0
         if word in destinations:
            ignorable = True
         elif word == 'bkmkstart':
            parsing_bkmkstart = True
            idx_stack.append({'start': out_count, 'end': -1, 'content': []})
         elif word == 'bkmkend':
            parsing_bkmkend = True
         elif ignorable:
            pass
         elif word in specialchars:
            out_count = out_append(out_count, out, specialchars[word])
         elif word == 'uc':
            ucskip = int(arg)
         elif word == 'u':
            c = int(arg)
            if c < 0: c += 0x10000
            if c > 127: out_count = out_append(out_count, out, chr(c)) #NOQA
            else: out_count = out_append(out_count, out, chr(c))
            curskip = ucskip
      elif hex: # \'xx
         if curskip > 0:
            curskip -= 1
         elif not ignorable:
            c = int(hex,16)
            if c > 127: out_count = out_append(out_count, out, chr(c)) #NOQA
            else: out_count = out_append(out_count, out, chr(c))
      elif tchar:
         if curskip > 0:
            curskip -= 1
         elif not ignorable:
            if parsing_bkmkstart:
               idx_stack[-1]['content'].append(tchar)
            elif parsing_bkmkend:
               current_bkmkend.append(tchar)
            else:
                out_count = out_append(out_count, out, tchar)

   return (bookmarks, ''.join(out))
