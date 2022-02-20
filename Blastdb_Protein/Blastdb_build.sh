# Create a BLAST database for a comparative reference protein set
makeblastdb -in Screened_Mouse_Protein_with_UniqueID.fa \
            -dbtype prot \
		    -out Mouse_protein_blast_index \
			-title Mouse_protein \
			-logfile Mouse_protein.makeblastdb.log

