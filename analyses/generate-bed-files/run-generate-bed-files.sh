#!/bin/bash

# Load necessary modules
module load python/3.9.9
module load bedtools/2.31.0

# Read root path
rootdir=$(realpath "./../..")
echo "$rootdir"

# Load files which are relevant to both blacklist and enhancer/promoter script
inputfai=$(cat ${rootdir}/project_parameters.Config.yaml | grep 'faidx_file_path:' | awk '{print $2}')
inputfai=${inputfai//\"/}  # Removes all double quotes
echo "$inputfai"

inputspecies=$(cat ${rootdir}/project_parameters.Config.yaml | grep 'species:' | awk '{print $2}')
inputspecies=${inputspecies//\"/}  # Removes all double quotes
echo "$inputspecies"

copy_files=$(cat ${rootdir}/project_parameters.Config.yaml | grep 'copy_files:' | awk '{print $2}')
copy_files=${copy_files//\"/}  # Removes all double quotes
echo "$copy_files"

copy_path=$(cat ${rootdir}/project_parameters.Config.yaml | grep 'copy_path:' | awk '{print $2}')
copy_path=${copy_path//\"/}  # Removes all double quotes
echo "$copy_path"

# Load T/F for running blacklist and enhancer/promoter
blacklist_boolean=$(cat ${rootdir}/project_parameters.Config.yaml | grep 'run_blacklist_step' | awk '{print $2}')
blacklist_boolean=${blacklist_boolean//\"/}  # Removes all double quotes
echo "$blacklist_boolean"

enh_promo_boolean=$(cat ${rootdir}/project_parameters.Config.yaml | grep 'run_enhancer_promoter_step' | awk '{print $2}')
enh_promo_boolean=${enh_promo_boolean//\"/}  # Removes all double quotes
echo "$enh_promo_boolean"

if [[ "$blacklist_boolean" == "TRUE" ]]; then
   inputbed=$(cat ${rootdir}/project_parameters.Config.yaml | grep 'blacklist_file_path:' | awk '{print $2}')
   inputbed=${inputbed//\"/}  # Removes all double quotes
   echo "$inputbed"

   outputpath=$rootdir/analyses/generate-bed-files/results
   echo "$outputpath"

   mkdir -p $outputpath

   outputbed=$outputpath/blacklist.bed
   echo $outputbed

   # Check if output file exists and if not then create it
   if [ ! -f "$outputbed" ]; then
       echo "$outputbed does not exist. Creating bed file."
       touch $outputbed
   fi

   # Run python script to get bed file with correctly named and formatted chromosomes
   # This script also checks for malformed lines in the input bed file
   if [ "$copy_files" == "TRUE" ]; then
      python $rootdir/analyses/generate-bed-files/01-generate-blacklist.py \
       --bed=$inputbed \
       --species=$inputspecies \
       --outputfile=$outputbed \
       --faidx=$inputfai \
       --copy=$copy_files \
       --copy_path=$copy_path
   else
      python $rootdir/analyses/generate-bed-files/01-generate-blacklist.py \
       --bed=$inputbed \
       --species=$inputspecies \
       --outputfile=$outputbed \
       --faidx=$inputfai \
       --copy=$copy_files
   fi
fi

if [[ "$enh_promo_boolean" == "TRUE" ]]; then
   # Define file paths and file names for input and output files and define any other parameters to pass to python script
   inputgff=$(cat ${rootdir}/project_parameters.Config.yaml | grep 'regulatory_file_path:' | awk '{print $2}')
   inputgff=${inputgff//\"/}  # Removes all double quotes
   echo "$inputgff"

   outputpath=$rootdir/analyses/generate-bed-files/results
   echo "$outputpath"

   mkdir -p $outputpath

   outputgff=$outputpath/regulatory.gff
   echo $outputgff

   # Check if output file exists and if not then create it
   if [ ! -f "$outputgff" ]; then
       echo "$outputgff does not exist. Creating gff file."
       touch $outputgff
   fi

   # Run python script to check chromosome names
   # This script also checks for proper formatting of input file
   # Note that input gff files can have entries for non-standard chromosome
   # But following the 10x workflow, only standard chromosomes are kept
   # Can explore adjusting this in the future if necessary
   if [ "$copy_files" == "TRUE" ]; then
      python $rootdir/analyses/generate-bed-files/02-generate-promoter-enhancer.py \
       --gff=$inputgff \
       --species=$inputspecies \
       --outputfile=$outputgff \
       --faidx=$inputfai \
       --outpath=$outputpath \
       --copy=$copy_files \
       --copy_path=$copy_path
   else
      python $rootdir/analyses/generate-bed-files/02-generate-promoter-enhancer.py \
       --gff=$inputgff \
       --species=$inputspecies \
       --outputfile=$outputgff \
       --faidx=$inputfai \
       --outpath=$outputpath \
       --copy=$copy_files
   fi
fi