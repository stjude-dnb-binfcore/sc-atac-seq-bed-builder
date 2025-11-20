#!/usr/bin/env python3

"""
This script will take an input blacklist bed file and then
(1) Check the formatting of the bed file is correct (i.e. it is not malformed)
(2) Check that chromosomes are named correctly for the corresponding reference genome fai file
(3) Check for chromosomes in blacklist file to exist in reference genome standard chromosomes (i.e. autosomal + sex + mitochondrial chromosomes) and filter non-standard chromosomes
(4) Write out bed file with correct chromosome names and chromosomes filtered

Based off of 10x Genomics code
See here: https://github.com/10XGenomics/cellranger-atac/blob/main/lib/python/reference.py
"""

import sys
import os
import argparse
import shutil

sys.dont_write_bytecode = True
import util.bed_functions as bf

###
# This function calls the subfunctions to check bed formatting and chromosome naming, do chromosome filtering, sort and keep unique bed entries
# Optionally can also copy output files to another directory as specified in the project_parameters.Config.yaml
def get_blacklist(bed_path, species, out_path, faidx_file, copy, copy_path):

    bf.clean_chr_name_file(bed_path, species, out_path)

    bf.sort_and_uniq_bed(out_path, faidx_file, cut_cols=True)

    if copy == "TRUE":
       shutil.copy(src=out_path, dst=copy_path)
###

###
# Define function to check for file to exist
def file_path(string):
	if os.path.isfile(string) | os.path.exists(string):
		return string
	else:
		raise FileNotFoundError(string)
###

# Define parser for arguments
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument('--bed', type=file_path, help='Input blacklist bed to use for generating blacklist reference bed file', required=True)
parser.add_argument('--species', type=str, help='Species for the corresponding reference genome that the blacklist is being generated for, expects either mouse or human as the input', required=True)
parser.add_argument('--outputfile', type=file_path, help='Path and filename to save the finalized bed file output to', required=True)
parser.add_argument('--faidx', type=file_path, help='Fasta index file for corresponding reference genome', required=True)
parser.add_argument('--copy', type=str, help='String indicating if results files should be copied', required=True)
parser.add_argument('--copy_path', type=file_path, help='Path to copy results files to', required=False)

#Convert argument strings to objects and assigns them as attributes of the namespace; e.g. --bed -> args.bed
args = parser.parse_args()

# Call function to get blacklist bed file
# Pass args input to the blacklist function
get_blacklist(args.bed, args.species, args.outputfile, args.faidx, 
			  args.copy, args.copy_path)