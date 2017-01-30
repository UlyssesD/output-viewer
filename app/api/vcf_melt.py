#!/usr/bin/env python
""" Melt a VCF file into a tab delimited set of calls, one per line

VCF files have all the calls from different samples on one line.  This
script reads vcf on stdin and writes all calls to stdout in tab delimited
format with one call in one sample per line.  This makes it easy to find
a given sample's genotype with, say, grep.
"""

import sys
import csv
import vcf
import re

if len(sys.argv) > 1:
    inp = file(sys.argv[1])
else:
    inp = sys.stdin
reader = vcf.VCFReader(inp)

filename = re.sub("(\.)(\w)*$", "", sys.argv[1])
out = csv.writer(open(filename + '_parsed.txt', 'w'), delimiter='\t')

formats = reader.formats.keys()
infos = reader.infos.keys()

#header = ["SAMPLE"] + formats + ['FILTER', 'CHROM', 'POS', 'REF', 'ALT', 'ID', 'QUAL'] \
#        + ['info.' + x for x in infos]
header = ["SAMPLE", "CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER"] + [x for x in infos] + formats 

out.writerow(header)


def flatten(x):
    if type(x) == type([]):
        x = ','.join(map(str, x))
    return x

for record in reader:
    info_row = [flatten(record.INFO.get(x, None)) for x in infos]
    fixed = [record.CHROM, record.POS, record.ID, record.REF, record.ALT, record.QUAL]

    for sample in record.samples:
        row = [sample.sample]
        # Format fields not present will simply end up "blank"
        # in the output
        row += fixed
        row += [record.FILTER or '.']
        row += info_row
        row += [flatten(getattr(sample.data, x, None)) for x in formats]
        
        out.writerow(row)
