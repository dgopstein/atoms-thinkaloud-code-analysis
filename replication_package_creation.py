import parse_snippets
import extract_rtf
import lib

import os
import pprint
import csv

output_dir = 'replication_packet'

#plt.ion()
pp = pprint.PrettyPrinter(indent=4)
pprn = pp.pprint

texts, bookmarks, snippets = parse_snippets.parse_interviews()
codes = [b for b in bookmarks if parse_snippets.is_code(b)]
overlaps = extract_rtf.all_overlaps(bookmarks)

# Write transcripts to text files
for subj_id, transcript in texts.items():
    with open(os.path.join(output_dir, 'transcript_'+str(subj_id)+'.txt'), 'w') as f:
        print(transcript,  file=f)

# Write codes to csv file
with open(os.path.join(output_dir, 'codes.csv'), 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['subject', 'start_offset', 'end_offset', 'code', 'text'])
    for code in codes:
        csv_writer.writerow([code['subject'], code['start'], code['end'], code['codename'], code.get('text')])
