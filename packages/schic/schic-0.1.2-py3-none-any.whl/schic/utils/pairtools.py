# -*- coding: utf-8 -*-
__author__ = "legendzdy@dingtalk.com"
"""
Author: legendzdy@dingtalk.com
Data: 20250725
Description:
pairtools.
"""
from basebio import run_command

def pairtools(input_R1, input_R2, reference, genome_size, prefix, threads=8):
    """
    map with minimap2.
    Args:
        input: input fasta file.
        reference: reference fasta file.
        output: output sam/bam file.
        threads: number of threads.
    """
    out_sam = prefix + ".aligned.sam"
    cmd = ["bwa", "mem", "-5SP", "-T0", "-t", str(threads), reference, input_R1, input_R2, ">", out_sam]
    run_command(" ".join(cmd), use_shell=True)

    out_pairs = prefix + ".pairs.gz"
    run_command(["pairtools", "parse", "-c", genome_size, "-o", out_pairs, out_sam])

    out_sorted = prefix + ".sorted.pairs.gz"
    run_command(["pairtools", "sort", "--nproc", str(threads), "-o", out_sorted, out_pairs])

    out_nodups = prefix + ".nodups.pairs.gz"
    out_dups = prefix + ".dups.pairs.gz"
    out_unmapped = prefix + ".unmapped.pairs.gz"
    out_stats = prefix + ".dedup.stats"
    run_command(["pairtools", "dedup", "--mark-dups", "--output", out_nodups, "--output-dups", out_dups, "--output-unmapped", out_unmapped, "--output-stats", out_stats, out_sorted])

    mapped_pairs = prefix + "_mapped.pairs"
    cmd = ["zcat", out_nodups, "|", "grep", "-v", "\"^#\"", "|", "awk", "-F", "\"\t\"", "{print $1,$2,$3,$4,$5,$6,$7,$8}", "OFS=\"\t\"", ">", mapped_pairs]
    run_command(" ".join(cmd), use_shell=True)

    
#     zcat {}.nodups.pairs.gz|grep -v "^#"|awk -F \"\t\" '{print \$1,\$2,\$3,\$4,\$5,\$6,\$7,\$8}' OFS=\"\t\" > {}_mapped.pairs

#     python ${SOFT}/get_qc.py -p ./{}.dedup.stats > ./{}.qc.txt
#     cat ${WKD}/${FORWORD}/{}_GRIDv1.flagstat.txt|awk 'NR==1{print \"total_reads_raw\t\"\$1}' > {}.total_reads.txt
#     cat {}.total_reads.txt {}.qc.txt > {}.temp.txt
#     cat {}.temp.txt| sed -e 's/,//g' \
#         -e 's/Total Read Pairs/Reads_with_linker/g' \
#         -e 's/Unmapped Read Pairs/Unmapped_Read_Pairs/g' \
#         -e 's/Mapped Read Pairs/Mapped_Read_Pairs/g' \
#         -e 's/PCR Dup Read Pairs/PCR_Dup_Read_Pairs/g' \
#         -e 's/No-Dup Read Pairs/No-Dup_Read_Pairs/g' \
#         -e 's/No-Dup Cis Read Pairs/Cis_Read_Pairs/g' \
#         -e 's/No-Dup Trans Read Pairs/Trans_Read_Pairs/g' \
#         -e 's/No-Dup Valid Read Pairs (cis >= 1kb + trans)/Valid_Read_Pairs/g' \
#         -e 's/Cis_Read_Pairs < 1kb/Cis1kb/g' \
#         -e 's/Cis_Read_Pairs >= 1kb/Cis1kb+/g' \
#         -e 's/Cis_Read_Pairs >= 10kb/Cis10kb+/g' |awk '{print \$1,\$2}' OFS=\"\t\" > {}.sample.txt
#     "