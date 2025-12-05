#!/usr/bin/env python3

# Code is (adapted) from the resources and codebase below
# https://github.com/10XGenomics/cellranger-atac/blob/main/lib/python/reference.py
# https://github.com/10XGenomics/cellranger-atac/blob/main/lib/python/tools/regions.py
# Credit: 10x genomics

import os
import shutil
import sys
import tempfile
import subprocess

from pybedtools import BedTool, MalformedBedLineError

###
def bed_format_checker(in_bed_file, faidx_file):
    """
    Given a bed file path, examine whether is it a valid bed format
    Examined items include: basic formatting, coordinate overflow, contig name is within reference and properly sorted
    :param in_bed_file: file path of input bed file
    :param faidx_file: fasta index file (.fai) file.
    :return:
    """
    if in_bed_file is None:
        return None

    # Read in fasta index and get contig names and lenghts
    all_contigs = []
    contig_lengths = {}
    with open(faidx_file) as faidx:
        for line in faidx:
            line = line.strip().split()
            contig_name, contig_length = line[0], line[1]

            all_contigs.append(contig_name)
            contig_lengths[contig_name] = int(contig_length)

    # Call function to check for malformed lines in bed file
    bediter = bed_format_checker_iter(in_bed_file)
    contig_iter = iter(all_contigs)  # contig order in the reference
    next_contig = next(contig_iter)

    # This will account for header lines at the beginning of the input bed file
    i = count_header_lines_bed(in_bed_file)

    # Check each bed entry to ensure contig names match fai names
    # Also check for appropriate contig lengths
    # And check that bed is sorted properly
    for bed in bediter:
        i += 1
        if bed.chrom not in contig_lengths:
            sys.exit('Malformed BED entry at line {} in {}: invalid contig name.'.format(i, in_bed_file))

        if bed.end > contig_lengths[bed.chrom]:
            if os.path.basename(in_bed_file) == 'blacklist.bed':
                pass
            else:
                sys.exit('Malformed BED entry at line {} in {}: Coordinate exceeds the length of the contig.'.format(i, in_bed_file))

        while bed.chrom != next_contig:
            try:
                next_contig = next(contig_iter)
            except StopIteration:
                sys.exit('Malformed BED entry at line {} in {}: contigs are not properly sorted according to the order in the reference fasta.'.format(i, in_bed_file))
###

###
def bed_format_checker_iter(in_bed_file):
    """
    Take a file path of a BED/GTF/GFF file and return a generator with BedTool built-in format checker
    :param in_bed_file:
    :return:
    """

    # Create iterator to parse input bed file
    bediter = iter(BedTool(in_bed_file))

    # This will account for header lines at the beginning of the input bed file
    i = count_header_lines_bed(in_bed_file)

    # Checks for appropriate bed formatting of each line and returns an error if malformed lines are encountered
    while True:
        i += 1
        try:
            row = next(bediter)
            yield row
        except MalformedBedLineError as e:
            e_is_too_long = '\n' if len(str(e)) > 80 else ''
            msg = "Malformed BED entry at line {} in {}: {}".format(i, in_bed_file, e_is_too_long)
            sys.exit(msg + str(e))
        except IndexError as e:
            if i == 1:
                msg = 'Invalid BED format for {}, please check the source.'.format(in_bed_file)
                sys.exit(msg)
            else:
                msg = "Malformed BED entry at line {} in {}: ".format(i, in_bed_file)
                sys.exit(msg + str(e))
        except StopIteration:
            break
###

###
def clean_chr_name(chrom, species, keep_nonstd=False):
    """
    match the input chrom string to the standard format used in the genome.fa.fai
    """

    # Define "standard" chromosome names based on species 
    # For the 2020 and 2024 atac references maintained in DNB binf core, the reference genomes always have the "chr" prefix and "chrM" naming for mitochondrial
    # Can explore expanding these options if needed in the department
    if species == "mouse":
        std_names = [str(i) for i in range(1, 20)] + ['M', 'X', 'Y']
    elif species == "human":
        std_names = [str(i) for i in range(1, 23)] + ['M', 'X', 'Y']

    # Strips prefix from input file chromosome names
    test_name = chrom.lstrip('chr')

    # Check for chromosome from input file to exist in "standard" name list and keep if found
    if test_name in std_names:
        return 'chr' + test_name

    # To handle differences for mitochondrial chromosome naming at MT naming can be common as well
    elif test_name == 'MT':
        return 'chr' + 'M'
    elif keep_nonstd:
        return test_name
    else:
        return None
###

###
def clean_chr_name_file(in_file, species, output_file):
    """
    given a tab-delimitated file, run clean_chr_name to clean the first column, which is the default chrom column
    """

    print("Filtering {}...".format(in_file))

    # Define temporary file to save output to
    tmp = tempfile.NamedTemporaryFile(dir=os.path.dirname(output_file), delete=False)

    # Call function to check for malformed bed file lines
    bediter = bed_format_checker_iter(in_file)

    # Call function to check chromosome naming format and filter out "non-standard" chromosomes
    for fields in bediter:
        
        chrom = clean_chr_name(str(fields.chrom), species)
        
        # Write out lines which pass the filtering for chromosome
        if chrom is not None:
            fields.chrom = chrom
            tmp.write(bytes('\t'.join(fields.fields) + '\n', encoding="ascii"))

    # Move temporary file to output file name as provided in the arguments
    shutil.move(tmp.name, output_file)
    tmp.close()
    print("done\n")
###

###
def count_header_lines_bed(in_file):
    """ Count the number of header lines in a bed file
        Header lines are defined as lines starting with "#" in the beginning of the file
        Comment lines with "#" that not in the header will not be counted
    """

    counter = 0
    with open(in_file) as file_in:
        for line in file_in:
            if line.startswith("#"):
                counter += 1
            else:
                break

    return counter
###

###
# Note: portions of the code related to other regulatory element types were (i.e. CTCF binding sites) were removed
def get_reg_elements(input_gff, faidx_file, output_path):

    # Do additional checks for proper formatting of the input gff file for consistency with bed formatting
    bed_format_checker(input_gff, faidx_file)

    # Parse gff to generate regulatory regions bed
    # Define output files for enhancers and promoters
    promoter_out = os.path.join(output_path, 'promoter.bed')
    enhancer_out = os.path.join(output_path, 'enhancer.bed')

    print("Parsing functional annotation bed files...")
    count = {'promoter': 0,
             'enhancer': 0}

    # Open output files to save results to
    with open(promoter_out, 'w') as pro, open(enhancer_out, 'w') as enh:

        # Create iterator and again check formatting of input file
        gtf_iter = bed_format_checker_iter(input_gff)

        for fields in gtf_iter:

            # 10x comment: 1based coord. from gtf/gff is accommodated in reader_iter
            # Fields in the input file will be defined by column number as the input file is expected to be in standard gff format
            # Chrom is 0, start is 3, end is 4, strand is 6
            # https://useast.ensembl.org/info/website/upload/gff.html
            
            reg_start = fields[3]
            reg_end = fields[4]

            # Save info from gff in bed formatting and column order
            # https://useast.ensembl.org/info/website/upload/bed.html
            row = [fields[0], reg_start, reg_end, '.', '.', fields[6]]

            # Filter input based on regulatory feature type to save enhancers and promoters
            # Region annotations are in last column, index 8
            # Note that the 10x code defined anything that wasn't a promoter or CTCF binding site as an enhancer, but it seems like the gff from ensembl includes other types of regulatory regions, so will specifically only include regions labeled as enhancer
            # https://useast.ensembl.org/info/genome/funcgen/data/regulatory-features.html
            test_str=fields[8]

            if test_str.endswith('Promoter'):
                count['promoter'] += 1
                pro.write('\t'.join(map(str, row)) + '\n')

            elif test_str.endswith('Enhancer'):
                count['enhancer'] += 1
                enh.write('\t'.join(map(str, row)) + '\n')               

    # Close files that were opened
    pro.close()
    enh.close()
    
    # Report counts of promoters and enhancers found in gff
    for region, n in count.items():
        print(f"    Parsed {n} {region} regions.")
    print("done")

    # Add sort and uniq for each bed file here
    sort_and_uniq_bed(promoter_out, faidx_file, cut_cols=False)
    sort_and_uniq_bed(enhancer_out, faidx_file, cut_cols=False)
###

###
def sort_and_uniq_bed(in_bed_file, faidx_file, cut_cols):
    """
    given a path of a bed file, sort bed file and remove duplicate rows
    ref_path is required to extract the chromosome orders from the genome.fa.fai
    """

    if in_bed_file.endswith('.gz'):
        sys.exit("Input bed file is gzip compressed, please decompress it first.\n")

    # Check for fai file to exist
    if not os.path.exists(faidx_file):
        sys.exit("Cannot find genome fasta index file.")

    input_bed = BedTool(in_bed_file)

    # Subset to chr, start, stop only if true
    if cut_cols == True:
        input_bed = input_bed.cut([0,1,2])

    # Open temporary file to save sorted results to
    with tempfile.NamedTemporaryFile(dir=os.path.dirname(in_bed_file), delete=False) as tmp:
        sorted_bed = input_bed.sort(g=faidx_file).saveas(tmp.name)

        # remove duplicate lines from sorted file and write to the original input bed file
        uniq_cmd = ['uniq', sorted_bed.fn]
        with open(in_bed_file, 'w') as out_file:
            subprocess.call(uniq_cmd, stdout=out_file)

        # clean up temporary files
        os.remove(tmp.name)
###