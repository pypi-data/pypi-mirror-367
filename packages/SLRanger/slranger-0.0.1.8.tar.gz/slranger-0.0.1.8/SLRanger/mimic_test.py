import re
import argparse
from email.policy import default

import pysam
import pandas as pd
# from ssw import AlignmentMgr
from pyssw.ssw_wrap import Aligner
from Bio.Seq import Seq
import random
import multiprocessing
from tqdm import tqdm
import time

def consensus(ref, query, cigar_string, ref_shift=0, query_shift = 0):
    """
    to get a concensus sequence as the longest cons of both sequence,
    and fill all disagreement with N
    for example,
    query:AAATA-TAGAA
    ref:  AAACACTA-AA
    cons: AAANANCANAA

    use query to get the con
    then get two chain file, 0 based
    """

    # pattern = re.compile('([0-9]*)([MIDNSHP=X])')
    pattern = re.compile(r"([0-9]+)b?'?([MIDNSHP=X])")
    query_out = []
    ref_out = []
    cons = []

    query_pos = query_shift
    ref_pos = ref_shift

    cigar_pattern = pattern.findall(cigar_string)
    for i, (length, code) in enumerate(cigar_pattern):
        if i == 0 or i == len(cigar_pattern) - 1:
            if code == "S":
                continue

        length = int(length)

        if code == "M":
            for i in range(length):
                q_s = query[query_pos].upper()
                try:
                    r_s = ref[ref_pos].upper()
                except IndexError as e:
                    print
                    "indexerror", ref_pos

                query_out.append(q_s)
                ref_out.append(r_s)

                cons.append(q_s) if q_s == r_s else cons.append("m")

                ref_pos += 1
                query_pos += 1

        elif code in "D":
            for i in range(length):
                r_s = ref[ref_pos]

                ref_out.append(r_s)
                query_out.append("-")
                cons.append("d")

                ref_pos += 1

        elif code in "IHS":
            for i in range(length):
                q_s = query[query_pos]

                query_out.append(q_s)
                ref_out.append("-")
                cons.append("i")
                query_pos += 1

    return "".join(cons)   # "".join(cons), "".join(query_out), "".join(ref_out)

def soft_processed(sequence, strand, cigar):
    """
    根据 strand 和 cigar 信息提取指定长度的序列部分。

    参数:
    - sequence (str): 原始的序列字符串。这个sequence已经被reverse处理过了，与正链一致，所以取序列的时候都从开头取起
    - strand (str): 链方向，"+" 或 "-"。
    - cigar (list of tuples): CIGAR 信息，表示为列表的元组 (operation, length)。
                              例如 [(4, 5), (0, 50)] 表示 5 bp 的 soft clipping，接着是 50 bp 的匹配。
    返回:
    - str: 根据条件截取后的序列。再多加两个碱基在后面
    """
    if not cigar:
        return ""  # Return empty string if no CIGAR info
    soft_clip_length = 0
    if strand == "+":
        if cigar[0][0] == 4:
            soft_clip_length = cigar[0][1]
    elif strand == "-":
        if cigar[-1][0] == 4:
            soft_clip_length = cigar[-1][1]

    if soft_clip_length >= 5:
        soft_seq = sequence[max(0, soft_clip_length - 13) : soft_clip_length + 2]
        align_seq = sequence[soft_clip_length + 2 : soft_clip_length + 52]
        return soft_seq, align_seq
    else:
        return "", ""


def ssw_wrapper(seq1, seq2, match=1, mismatch=1, gap_open=1, gap_extend=1):
    """
    parameter are write inside the function
    seq1 is ref and seq2 is query
    # todo : leave a api to change matrix
    """

    ref_seq = str(seq1)
    read_seq = str(seq2)
    # reduce the gap open score from 3 to 1 for nanopore reads
    aligner = Aligner(ref_seq,
                      match, mismatch, gap_open, gap_extend,
                      report_cigar=True, )

    aln = aligner.align(read_seq)  # min_score=20, min_len=10)

    return aln

def update(*a):
    if a[0] is not None:
        outfile.write(a[0])
    pbar.update(1)

def calculation_per_process(item):
    query_name = item[0]
    query_seq = item[1]
    strand = item[2]
    cigartuples = item[3]

    soft_seq, align_seq = soft_processed(query_seq, strand, cigartuples)

    if len(soft_seq) > 0:
        try:
            soft_seq_re = str(Seq(soft_seq).reverse_complement())
            sw_aln = ssw_wrapper(align_seq, soft_seq_re)  # score>10,
            sw_score = sw_aln.score
            ref_start = sw_aln.ref_begin
            ref_end = sw_aln.ref_end
            read_start = sw_aln.query_begin
            read_end = sw_aln.query_end + 1
            sw_cigar = sw_aln.cigar_string

            corrected_sequence_sw = soft_seq_re[read_start:read_end]

            seq_s_length = len(corrected_sequence_sw)
        except Exception as e:
            print(e)
        if seq_s_length >= 7 and sw_score > 8:
            try:
                sw_ref = align_seq[ref_start:ref_end]

                # print("\n".join(consensus(corrected_sequence_sw, sw_ref, sw_cigar, 0)))
                # last_three_chars = corrected_sequence_sw[-3:]
                con_seq = consensus(sw_ref, corrected_sequence_sw, sw_cigar, 0)

                SL_sw_dict = {'query_name': query_name,
                              'strand': strand,
                              'align_start': ref_start,
                              'align_end': ref_end,
                              'consensus': con_seq,
                              'sw_score': sw_score
                              }
                mes = '\t'.join([str(value) for value in SL_sw_dict.values()]) + "\n"
                return mes
            except Exception as e:
                print(e)
        else:
            return None
    else:
        return None

def main(args):
    global outfile, pbar
    df = pd.read_csv(args.SL_info, sep='\t')
    df_solid = df[df['SL_score'] >= 6.5]
    del df
    read_list = df_solid['query_name'].tolist()
    read_list = set(read_list)
    bam_file = pysam.AlignmentFile(args.input_bam, 'rb')
    timestamp = int(time.time())
    # outfile = open(args.outfile, "w")
    tmp_output_name = f"tmp_{timestamp}.csv"
    outfile = open(tmp_output_name, "w")
    outfile.write(
        "query_name\tstrand\talign_start\taligned_end\tconsensus\tsw_score\n")

    print('Loading the BAM file')
    bam_list = []
    for read in bam_file.fetch():
        if read.is_supplementary or read.is_secondary:
            continue
        query_name = read.query_name
        if query_name in read_list:
            continue
        full_query_sequence = read.query_sequence
        if read.is_reverse:
            query_seq = str(Seq(full_query_sequence).reverse_complement())   # 序列映射到负链，需要反向互补处理
            strand = '-'
        else:
            query_seq = full_query_sequence    # 序列映射到正链，直接使用
            strand = '+'
        bam_list.append([query_name, query_seq, strand, read.cigartuples])
    bam_file.close()
    pbar = tqdm(total=len(bam_list), position=0, leave=True)
    with multiprocessing.Pool(processes=args.cpu) as pool:
        for item in bam_list:
            pool.apply_async(calculation_per_process, args=(item,), callback=update)
        pool.close()
        pool.join()
    pbar.close()
    outfile.close()
    df = pd.read_csv(tmp_output_name,sep='\t')
    df.sort_values(by=['query_name'], inplace=True)
    df.to_csv(args.outfile, index=False,sep='\t')
    print('Finished')

if __name__ == '__main__':
    global bamfile

    parser = argparse.ArgumentParser(
        description="help to know spliced leader and distinguish SL1 and SL2")
    parser.add_argument("-b", "--input_bam", type=str, metavar="",
                        default="/t4/ywshao/cbr_cni_directrna/raw_data/Cel/dorado_result/minimap_bam/Cel_EMBO_F.bam",
                        # default="/t3/ywshao/cbr_cni_drs/cel_cdna_Bernard/genomic/SSP/SRR18584063/results/observed_quality/asp-4.bam",
                        help="input the bam file")
    parser.add_argument("-i", "--SL_info", type=str, metavar="",
                        default="/t4/ywshao/cbr_cni_directrna/raw_data/cbn_SL/0401/cel_embo.txt",
                        help="input the SL info file")
    parser.add_argument("-o", "--outfile", type=str, metavar="",
                        default="/t4/ywshao/cbr_cni_directrna/raw_data/cbn_SL/0401/Cel_EMBO_mimic_t.txt",
                        help="output the SL info file")
    parser.add_argument("-t", "--cpu", type=int,
                        default=64,
                        help="number if CPU")
    args = parser.parse_args()
    main(args)
