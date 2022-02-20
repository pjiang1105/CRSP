#!/usr/bin/env python

import sys
import optparse

def main():
    usage = "Usage: %prog [options] < blast_tophits > map"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-e", "--e-value", dest="max_e_value",
                      type="float", default=1e-5, metavar="E-VALUE",
                      help="Maximum e-value of BLAST top hit to use in map")
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("Invalid number of arguments")
    tophits_to_map(sys.stdin, sys.stdout, options.max_e_value)

def tophits_to_map(tophit_in_stream, map_out_stream, max_e_value):
    for record in blast_tophit_reader(tophit_in_stream):
        if float(record["e_value"]) <= max_e_value:
            out_fields = [record["query_id"], record["subject_id"]]
            #print >>map_out_stream, "\t".join(out_fields) # Python 2
            print("\t".join(out_fields), file=map_out_stream) # Python 3

def blast_tophit_reader(stream):
    header_line = stream.readline()
    field_names = header_line.rstrip("\r\n").split("\t")
    for line in stream:
        fields = line.rstrip("\r\n").split("\t")
        yield dict(zip(field_names, fields))

if __name__ == "__main__":
    main()
