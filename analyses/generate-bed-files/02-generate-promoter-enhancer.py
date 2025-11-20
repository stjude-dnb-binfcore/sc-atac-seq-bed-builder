#!/usr/bin/env python3

"""
This script will take an input gff file of regulatory elements and then
(1) Check the formatting of the gff file is consistent with bed formatting (i.e. it is not malformed for the bed format)
(2) Check that chromosomes are named correctly for the corresponding reference genome fai file
(3) Check for chromosomes in gff file to exist in reference genome standard chromosomes (i.e. autosomal + sex + mitochondrial chromosomes)
(4) Check further that the formatting of the gff file is consistent with a bed file (including checking basic formatting, contig length, and other formatting)
Once formatting of gff file is fully confirmed to be consistent with bed formatting and is properly sorted and duplicates are removed, then:
(5) Separate regulatory gff into enhancer and promoter entries based on annotation in the gff file
(6) Write out final beds file, one for promoters, one for enhancers

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
# This function calls the subfunctions to check gff/bed formatting and chromosome naming, do chromosome filtering, filter regulatory files into enhancer and promoter bed files, sort and keep unique bed entries
# Optionally can also copy output files to another directory as specified in the project_parameters.Config.yaml
def get_gff(input_gff, species, out_file, faidx_file, out_path, copy, copy_path):

    bf.clean_chr_name_file(input_gff, species, out_file)
	
    bf.sort_and_uniq_bed(out_file, faidx_file, cut_cols=False)
	
    bf.get_reg_elements(out_file, faidx_file, out_path)
    
    if copy == "TRUE":
       enh = os.path.join(out_path,"enhancer.bed")
       promo = os.path.join(out_path,"promoter.bed")

       shutil.copy(src=enh, dst=copy_path)
       shutil.copy(src=promo, dst=copy_path)

	# Remove regulatory gff file used as intermediate file
    os.remove(out_file)
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
parser.add_argument('--gff', type=file_path, help='Regulatory gff file to use for generating the gff file with correct chromosome naming', required=True)
parser.add_argument('--species', type=str, help='Species for the corresponding reference genome that the enhancer and promoter bed files are being generated for, expects either mouse or human as the input', required=True)
parser.add_argument('--outputfile', type=file_path, help='Path and filename to save the output gff file to', required=True)
parser.add_argument('--faidx', type=file_path, help='Fasta index file for corresponding reference genome', required=True)
parser.add_argument('--outpath', type=file_path, help='Path to save the finalized gff file output to', required=True)
parser.add_argument('--copy', type=str, help='String indicating if results files should be copied', required=True)
parser.add_argument('--copy_path', type=file_path, help='Path to copy results files to', required=False)

#Convert argument strings to objects and assigns them as attributes of the namespace; e.g. --gff -> args.gff
args = parser.parse_args()

# Call function to get gff file and check chromosome naming
# Use arguments from user to pass input to the get_gff function
get_gff(args.gff, args.species, args.outputfile, args.faidx, args.outpath,
		args.copy, args.copy_path)