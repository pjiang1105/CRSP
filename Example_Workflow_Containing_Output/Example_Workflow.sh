#!/bin/bash -x

# You will need to have the following programs installed and in your PATH
# - cd-hit-est (https://github.com/weizhongli/cdhit)
# - NCBI-BLAST+ (ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/)
# - RSEM (http://deweylab.github.io/RSEM/)
# - Bowtie (http://bowtie-bio.sourceforge.net/)


# Merge multiple transcriptome assemblies, prepending a label to contigs
# from each assembly to avoid name collisions
python ../src/crsp_merge_assemblies.py assembly_1 ./User_Assembly_Files/Trinity_assembly_1.fasta \
                         assembly_2 ./User_Assembly_Files/Trinity_assembly_2.fasta \
                         > merged_assembly.fasta

# Create a non-redundant transcriptome assembly using cd-hit-est
cd-hit-est -M 200000 -T 0 -i merged_assembly.fasta -o non_redundant_assembly.fasta -c 1 \
     > reduce_assembly.log


# Create a BLAST database for a comparative reference protein set [please see the folder: Blastdb_Protein]
# CRSP (default) has build the mouse protein blastdb (the users can build their own blastdb) 
# makeblastdb -in ./Blastdb_Protein/Screened_Mouse_Protein_with_UniqueID.fa \
#             -dbtype prot \
#  	   	      -out ./Blastdb_Protein/Mouse_protein_blast_index \
#		 	  -title mouse_protein \
#			  -logfile mouse_protein.makeblastdb.log



# Run BLAST+ locally on the non-redundant assemlby and the comparative protein set
blastx \
    -num_threads 96 \
    -db ./Blastdb_Protein/Mouse_protein_blast_index \
    -outfmt 6 \
    < non_redundant_assembly.fasta \
    > mouse_protein.blast \
    2> mouse_protein.blast.log


# Extract the best BLAST hit for each contig
../src/crsp_blast_tophit.py < mouse_protein.blast > mouse_protein.tophits

# Create a mapping from contigs to comparative reference proteins with the given e-value threshold
../src/crsp_tophits_to_map.py -e 0.00001 < mouse_protein.tophits > contig_to_mouse_protein.map


# Prepare an RSEM reference using the non-redundant assembly
rsem-prepare-reference \
    --bowtie \
    non_redundant_assembly.fasta \
    rsem_reference \
    &> rsem_prepare_reference.log

# Compute contig expression levels using RSEM | The example is for paired end reads. For single end reads please see RSEM website: http://deweylab.github.io/RSEM/
rsem-calculate-expression \
    --bowtie-n 2 \
    --no-bam-output \
    --paired-end \
    ./User_RNASeq_Files/Sample_1.R1.fastq \
    ./User_RNASeq_Files/Sample_1.R2.fastq \
    rsem_reference \
    Sample_1 \
    &> rsem_calculate_expression.log

# Map contig expression levels to comparative reference protein expresion levels
../src/crsp_map_abundance_estimates.py \
    contig_to_mouse_protein.map \
    < Sample_1.genes.results \
    > Sample_1.proteins.results

# Map protein expression levels to gene symbol expresion levels
../src/crsp_map_abundance_estimates.py \
    ./Blastdb_Protein/Mouse_Protein_UniqueID_to_Symbol.map \
    < Sample_1.proteins.results \
    > Sample_1.gene_symbols.results
    
# *** Final results (file): Sample_1.gene_symbols.results ***





