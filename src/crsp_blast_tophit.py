#!/usr/bin/env python

import sys
import collections
import itertools

blast_fields = ["q_id", "s_id", "ident", "align_len", "mismatches", "gaps",
                "q_beg", "q_end", "s_beg", "s_end", "e_val", "bit_score"]
BLASTRecord = collections.namedtuple("BLASTRecord", blast_fields)

def blast_reader(stream):
    for line in stream:
        yield BLASTRecord(*line.split())

def hit_orientation(hit):
    is_forward_q = int(hit.q_beg) <= int(hit.q_end)
    is_forward_s = int(hit.s_beg) <= int(hit.s_end)
    return '+' if is_forward_q == is_forward_s else '-'

fields = ["query_id", "subject_id", "e_value", "orientation"]
print("\t".join(fields))

all_records = blast_reader(sys.stdin)
for query_id, records in itertools.groupby(all_records, lambda rec: rec.q_id):
    top_hit = next(records)
    rec = {"query_id": top_hit.q_id,
           "subject_id": top_hit.s_id,
           "e_value": top_hit.e_val,
           "orientation": hit_orientation(top_hit)}
    print("\t".join([str(rec[field]) for field in fields]))
