#!/usr/bin/env python

import sys
import optparse
import collections

import fasta

def main():
    usage = "Usage: %prog [options] refseq_protein.fasta gene2accession_filepath"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-i", "--minimum-identity", dest="min_identity",
                      type="float", default=0.95, metavar="FRACTION",
                      help="Minimum fractional identity between a pair of "
                      "sequences required for them to be considered redundant")
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Invalid number of arguments")
    fasta_filename, gene2accession_filepath = args

    seq_ids = list(sequence_ids_from_fasta_file(fasta_filename))
    gis = map(gi_from_seq_id, seq_ids)
    gi_to_seq_id_map = dict(zip(gis, seq_ids))
    gene2accession_records = gene2accession_records_from_file(gene2accession_filepath)
    output_seq_id_to_gene_symbol_map(gi_to_seq_id_map, gene2accession_records)

def output_seq_id_to_gene_symbol_map(gi_to_seq_id_map, gene2accession_records):
    mapped_seq_ids = set()
    for rec in gene2accession_records:
        seq_id = gi_to_seq_id_map.get(rec.protein_gi, None)
        if seq_id and seq_id not in mapped_seq_ids:
            print("\t".join([seq_id, rec.Symbol]))
            mapped_seq_ids.add(seq_id)
    
def sequence_ids_from_fasta_file(filename):
    with open(filename) as f:
        for rec in fasta.Reader(f):
            yield rec.title.split()[0]

def gi_from_seq_id(seq_id):
    return seq_id.split('|')[1]
            
gene2accession_field_names_string = "tax_id GeneID status RNA_nucleotide_accession.version RNA_nucleotide_gi protein_accession.version protein_gi genomic_nucleotide_accession.version genomic_nucleotide_gi start_position_on_the_genomic_accession end_position_on_the_genomic_accession orientation assembly mature_peptide_accession.version mature_peptide_gi Symbol"
gene2accession_field_names = gene2accession_field_names_string.replace('.', '_').split()
Gene2AccessionRecord = collections.namedtuple("Gene2AccessionRecord", 
                                              gene2accession_field_names)
def gene2accession_records_from_file(filename):
    with open(filename) as f:
        for line in f:
            if not line.startswith("#"):
                yield Gene2AccessionRecord(*line.rstrip("\r\n").split("\t"))

if __name__ == "__main__":
    main()
