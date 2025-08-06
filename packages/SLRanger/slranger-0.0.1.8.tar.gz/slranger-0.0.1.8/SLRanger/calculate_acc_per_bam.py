import numpy as np
import pandas as pd
import pysam
import re

def identify_match(cigar):
    # Identifies the number of matching bases in a read from its CIGAR string.
    cigar_mat = re.findall(r"\d+M", cigar)
    base_num_mat = sum(int(i[:-1]) for i in cigar_mat)
    return base_num_mat

def identify_insertion(cigar):
    # Identifies the number of inserted bases in a read from its CIGAR string.
    cigar_ins = re.findall(r"\d+I", cigar)
    base_num_ins = sum(int(i[:-1]) for i in cigar_ins)
    return base_num_ins

def identify_deletion(cigar):
    # Identifies the number of deleted bases in a read from its CIGAR string.
    cigar_del = re.findall(r"\d+D", cigar)
    base_num_del = sum(int(i[:-1]) for i in cigar_del)
    return base_num_del

def identify_substitution(md):
    # Identifies the number of substitutions in a read from its MD tag.
    return len(re.findall(r"\d+[ATCG]", md))


def observed_accuracy_worker(bam_file):
    bamfile = pysam.AlignmentFile(bam_file, 'rb')
    acc_list=[]
    for read in bamfile.fetch():
        if read.is_secondary or read.is_supplementary:
            continue
        # filter the unmapped reads
        if read.flag == 4:
            continue
        else:
            read_ID = read.query_name
            read_cigar = read.cigarstring
            read_md = read.get_tag("MD")

            # count the number of matched and mismatched base
            Ins = identify_insertion(read_cigar)
            Del = identify_deletion(read_cigar)
            Sub = identify_substitution(read_md)
            Mat = identify_match(read_cigar) - Sub

            # check the presence of supplementary reads
            if read.has_tag("SA"):
                continue
            else:
                # calculate the observed accuracy and identification
                total = Ins + Del + Sub + Mat
                Acc = Mat / total if total > 0 else 0
                Iden = Mat / (Mat + Sub) if (Mat + Sub) > 0 else 0
                acc_list.append(Acc)

    bamfile.close()
    print(bam_file,',',np.mean(acc_list))
    # print('Finished')
input_bam=[
# '/t4/ywshao/cbr_cni_directrna/raw_data/Cel/dorado_result/minimap_bam/Cel_EMBO_F.bam',
# '/t4/ywshao/cbr_cni_directrna/raw_data/Cel/dorado_result/minimap_bam/Cel_L1_F.bam',
# '/t4/ywshao/cbr_cni_directrna/raw_data/Cel/dorado_result/minimap_bam/Cel_YA_F.bam',
# '/t3/ywshao/cbr_cni_drs/cel_PRJEB31791/mapped_dir/L1_F.bam',
# '/t3/ywshao/cbr_cni_drs/cel_PRJEB31791/mapped_dir/L2_F.bam',
# '/t3/ywshao/cbr_cni_drs/cel_PRJEB31791/mapped_dir/L3_F.bam',
# '/t3/ywshao/cbr_cni_drs/cel_PRJEB31791/mapped_dir/L4_F.bam',
# '/t3/ywshao/cbr_cni_drs/cel_PRJEB31791/mapped_dir/adult_F.bam',
# '/t3/ywshao/cbr_cni_drs/cel_PRJEB31791/mapped_dir/male_F.bam',
# '/t3/ywshao/cbr_cni_drs/cel_PRJEB31791/mapped_dir/young_adult_F.bam',
# '/t3/ywshao/cbr_cni_drs/Brugia/SRR23886071/SRR23886071_F.bam',
    '/t3/ywshao/cbr_cni_drs/human/SRR32418660/SRR32418660_F.bam'
]
for item in input_bam:
    observed_accuracy_worker(item)