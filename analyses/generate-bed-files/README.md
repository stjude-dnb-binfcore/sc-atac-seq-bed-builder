# Pipeline for generating reference BED files for blacklist, enhancer, and promoter regions for single-cell ATAC (scATAC-Seq) 10x Genomics reference genomes


## Usage

The `run-generate-bed-files.sh` script is designed to run two scripts: 
   - `01-generate-blacklist.py`: To generate a properly formatted and filtered BED file (`blacklist.bed`) for blacklist regions for the reference genome of interest. 
   - `02-generate-promoter-enhancer`.py: To generate properly formatted BED files for enhancer and promoter regions (`enhancer.bed` and `promoter.bed`, respectively) for the reference genome of interest.

Users can run both scripts or select to execute only one by setting the `run_blacklist_step` and `run_enhancer_promoter_step` parameters in the `project_parameters.Config.yaml` file.

Output files are stored in the `./results` directory by default. To copy the output files to a specific location (such as the directory containing your reference genome), set the `copy_files` and `copy_path` parameters in the `project_parameters.Config.yaml` file.

Parameters for input data files and run options should be specified in the `project_parameters.Config.yaml` file located at the `root_dir`.


### Run module by using LSF on St. Jude HPC

To run the scripts in this module sequentially using LSF on HPC, please run the following command from an interactive compute node:

```
bsub < lsf-script.txt
```

Please note that this will run the analysis module by submitting an lsf job on HPC. We are using `python/3.9.9` and `bedtools/2.31.0` as available on St. Jude HPC. Also note that this module is currently organized to run only in the St. Jude HPC environment. Future improvements are planned to make the module usable across compute environment beyond St. Jude HPC.


### Run module on an interactive session on St. Jude HPC

To run the scripts in this module sequentially on an interactive session on HPC, please run the following command from an interactive compute node:

```
bash run-generate-bed-files.sh
```


## Folder content

This folder contains scripts tasked to generate reference BED files for single-cell ATAC (scATAC-Seq) data analysis in 10X Genomics data. These scripts were adapted from existing code from 10x Genomics. For more information, please see [here](https://github.com/10XGenomics/cellranger-atac/blob/main/lib/python/reference.py) and [here](https://github.com/10XGenomics/cellranger-atac/blob/main/lib/python/tools/regions.py).


## Folder structure 

The structure of this folder is as follows:

```
├── 01-generate-blacklist.py
├── 02-generate-promoter-enhancer.py
├── lsf-script.txt
├── README.md
├── results
|   ├── blacklist.bed
|   ├── enhancer.bed
|   └── promoter.bed
├── run-generate-bed-files.sh
└── util
    └── bed_functions.py
```