#!/usr/bin/env python

import sys
import optparse
import collections
import itertools

def main():
    usage = "Usage: %prog [options] map_file < rsem_results > mapped_rsem_results"
    parser = optparse.OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Invalid number of arguments")
    map_filename = args[0]
    entity_map = map_from_file(map_filename)
    map_abundance_estimates(sys.stdin, sys.stdout, entity_map)

def map_from_file(filename):
    with open(filename) as f:
        return dict([line.rstrip("\r\n").split("\t") for line in f])

def map_abundance_estimates(rsem_in_stream, rsem_out_stream, entity_map):
    print("\t".join(rsem_fields), file=rsem_out_stream) # python 3
    record_entity_map = RecordEntityMap(entity_map)
    rsem_records = list(rsem_reader(rsem_in_stream))
    sorted_rsem_records = sorted(rsem_records, key=record_entity_map)
    mapped_records = []
    for id, records in itertools.groupby(sorted_rsem_records, record_entity_map):
        if id != '':
            mapped_records.append(sum_records(id, list(records)))
    normalize_records(mapped_records)
    for record in mapped_records:
        print("\t".join(map(str, [record[name] for name in rsem_fields])))
        
rsem_fields = ["gene_id", "transcript_id(s)",
               "length", "effective_length",
               "expected_count", "TPM", "FPKM"]
rsem_field_types = [str, str,
                    float, float,
                    float, float, float]
            
def rsem_reader(stream):
    header_line = stream.readline()
    field_names = header_line.rstrip("\r\n").split("\t")
    assert(field_names == rsem_fields)
    for line in stream:
        fields = line.rstrip("\r\n").split("\t")
        yield dict([(k, t(f)) for k, t, f in zip(rsem_fields,
                                                 rsem_field_types,
                                                 fields)])

class RecordEntityMap:
    def __init__(self, entity_map):
        self.entity_map = entity_map
    def __call__(self, record):
        return self.entity_map.get(record["gene_id"], '')

def records_field(records, field_name):
    return [record[field_name] for record in records]
    
def sum_records(id, records):
    total_count = sum(records_field(records, "expected_count"))
    total_eff_length = sum(records_field(records, "effective_length"))
    return {"gene_id": id,
            "transcript_id(s)": ",".join(records_field(records, "gene_id")),
            "length": sum(records_field(records, "length")),
            "effective_length": total_eff_length,
            "expected_count": total_count,
            "TPM": total_count / total_eff_length,
            "FPKM": total_count / (total_eff_length * 1e-3)}

def normalize_records(records):
    fpkm_normalization = sum(records_field(records, "expected_count")) * 1e-6
    tpm_normalization = sum(records_field(records, "TPM")) * 1e-6
    for record in records:
        record["FPKM"] /= fpkm_normalization
        record["TPM"] /= tpm_normalization
    
if __name__ == "__main__":
    main()
