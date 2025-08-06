# scHIC

scHIC is a Python package for analyzing ONT cDNA sequencing data. It provides a set of modules for identifying new genes and isoforms

# Table of Contents
<!-- TOC -->

- [1. scHIC](#1-scHIC)
- [2. Table of Contents](#2-table-of-contents)
- [3. Overview](#3-overview)
- [4. Requirements](#4-requirements)
- [5. scHIC modules](#5-scHIC-modules)
    - [5.1. scHIC gene](#51-scHIC-gene)
    - [5.2. Usage](#52-usage)
    - [5.3. scHIC isoform](#53-scHIC-isoform)
    - [5.4. Usage](#54-usage)
    - [5.5. scHIC m6A sites](#55-scHIC-m6a-sites)
    - [5.6. Usage](#56-usage)
    - [5.7. scHIC new mRNA](#57-scHIC-new-mrna)
    - [5.8. Usage](#58-usage)
- [6. Scripts](#6-scripts)
    - [6.1. detect5EU.py](#61-detect5eupy)
    - [6.2. Usage](#62-usage)
- [7. Docker](#7-docker)
- [8. Conda Environment](#8-conda-environment)
- [9. Cite scHIC](#9-cite-scHIC)

<!-- /TOC -->

# Overview



# Requirements

1. Python 3.8+


# scHIC modules



## scHIC gene

## test
```bash
nohup python ./modifications.py -i ./treat.pass.fq.gz -s Treat.sam -b genes.bed -o test.treat.mod.bed > test.treat.mod.log 2>&1 &
nohup scHIC detectMod -i ./treat.pass.fq.gz -s Treat.sam -b genes.bed -o test.treat.mod.detectMod.bed > test.treat.mod.detectMod.log 2>&1 &
nohup scHIC detectMod -i ../input/LPS3/pass.fq.gz -s ../01_map_gene/LPS3_gene.sam -b ../reference/genes/genes.bed -o ./LPS3_modfi.bed &
```

## Usage

`scHIC.py gene -i sample -f genome.cdna.fa -e 0.005 -o gene`

## scHIC isoform

## Usage

`scHIC.py isoform -i sample -f genome.cdna.fa -e 0.005 -o isoform`

## scHIC m6A sites

## Usage

`scHIC.py detectm6A -i sample -f genome.cdna.fa -e 0.005 -o m6A`

## scHIC new mRNA

## Usage

`scHIC.py detectnewmRNA -i sample -f genome.cdna.fa -e 0.005 -o newmRNA`

# Scripts

We provide a set of standalone scripts for 5EU detection and quantification.

## detect5EU.py

This script detects 5' untranslated regions (5EU) from the ONT direct RNA sequencing data.

## Usage

`python detect5EU.py -i sample.fastq -o 5EU.bed`

# Docker

If the user has docker installed, the following command can be used to run the pipeline in a docker container:

```
docker run -v /path/to/data:/data -it scHIC/scHIC:latest /bin/bash
```

# Conda Environment

If the user has conda installed, the following command can be used to create a conda environment for scHIC:

1. Install conda
2. Create a new conda environment: `conda create -n scHIC python=3.6`
3. Activate the environment: `conda activate scHIC`
4. Install the required packages: `conda install -c bioconda minimap2 samtools bedtools flair tombo mines`
5. Install the required python packages: `pip install pandas numpy scipy sklearn matplotlib seaborn pysam`
6. Clone the scHIC repository: `git clone https://github.com/epibiotek/scHIC.git`
7. Run the pipeline: `python scHIC/scHIC.py gene -i sample -f genome.cdna.fa -e 0.005 -o gene`

# Cite scHIC

If you use scHIC in your research, please cite the following paper: