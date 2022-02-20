#!/usr/bin/env python

import sys,os

src_dir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, src_dir)

import fasta


def main():
    #if len(sys.argv) < 3 | (len(sys.argv) % 2) != 1:
        #print >>sys.stderr, "Usage: %s label1 assembly1.fasta [label2 assembly2.fasta ...] > merged_assembly.fasta" % sys.argv[0]    # python 2
        #print("Usage: %s label1 assembly1.fasta [label2 assembly2.fasta ...] > merged_assembly.fasta" % sys.argv[0], file=sys.stderr) # python3
        #sys.exit(1)
    labels = sys.argv[1::2]
    assembly_fasta_filenames = sys.argv[2::2]
    merge_assemblies(labels, assembly_fasta_filenames, sys.stdout)
    
def merge_assemblies(labels, assembly_fasta_filenames, out_stream):
    writer = fasta.Writer(out_stream)
    for label, fasta_filename in zip(labels, assembly_fasta_filenames):
        with open(fasta_filename) as fasta_file:
            reader = fasta.Reader(fasta_file)
            add_prefix_to_fasta_records(reader, writer, label)

def add_prefix_to_fasta_records(reader, writer, prefix):
    for rec in reader:
        writer.write(fasta.Record("%s_%s" % (prefix, rec.title), rec.sequence))

if __name__ == "__main__":
    main()
