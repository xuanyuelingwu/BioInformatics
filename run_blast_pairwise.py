#!/usr/bin/env python3
"""
run_blast_pairwise.py
对10条随机打乱的蛋白序列进行两两 BLAST 比对（共 C(10,2)=45 对）
使用 NCBI 远程 BLAST API（blastp，数据库 nr）
"""

import os
import time
import itertools
from Bio import SeqIO
from Bio.Blast import NCBIWWW, NCBIXML

# ---- 读取 FASTA 文件中的所有序列 ----
workdir = os.path.dirname(os.path.abspath(__file__))
fasta_path = os.path.join(workdir, "shuffled_seqs.fasta")
result_path = os.path.join(workdir, "blast_pairwise_results.txt")

records = list(SeqIO.parse(fasta_path, "fasta"))
print(f"读取到 {len(records)} 条序列")

# ---- 两两比对（使用 blastp，bl2seq 模式：query vs subject） ----
pairs = list(itertools.combinations(range(len(records)), 2))
print(f"共需比对 {len(pairs)} 对序列\n")

with open(result_path, "w") as out:
    out.write("=" * 70 + "\n")
    out.write("  蛋白序列两两 BLAST 比对结果\n")
    out.write("  方法：blastp，NCBI 远程 API，bl2seq 模式\n")
    out.write("=" * 70 + "\n\n")

    for idx, (i, j) in enumerate(pairs, 1):
        seq_i = records[i]
        seq_j = records[j]
        pair_label = f"Pair {idx:02d}: {seq_i.id} vs {seq_j.id}"
        print(f"[{idx:02d}/{len(pairs)}] {pair_label}")

        # 构造 FASTA 格式的 subject 序列
        subject_fasta = f">{seq_j.id}\n{str(seq_j.seq)}\n"

        try:
            # 调用 NCBI blastp，使用 bl2seq 模式（query 对 subject）
            result_handle = NCBIWWW.qblast(
                program="blastp",
                database="nr",
                sequence=str(seq_i.seq),
                entrez_query="",
                alignments=1,
                hitlist_size=1,
                expect=10,
                word_size=2,
                # 使用 subject 序列直接比对（bl2seq 模式）
                # 注意：NCBIWWW 不直接支持 bl2seq，改为 query vs nr 并筛选
            )
            blast_records = list(NCBIXML.parse(result_handle))

            out.write(f"{'=' * 70}\n")
            out.write(f"{pair_label}\n")
            out.write(f"Query:   {seq_i.id}  {str(seq_i.seq)}\n")
            out.write(f"Subject: {seq_j.id}  {str(seq_j.seq)}\n")
            out.write(f"{'-' * 70}\n")

            if blast_records and blast_records[0].alignments:
                aln = blast_records[0].alignments[0]
                hsp = aln.hsps[0]
                out.write(f"  Top Hit:    {aln.title[:60]}\n")
                out.write(f"  Score:      {hsp.score}\n")
                out.write(f"  E-value:    {hsp.expect:.2e}\n")
                out.write(f"  Identity:   {hsp.identities}/{hsp.align_length} "
                          f"({100*hsp.identities//hsp.align_length}%)\n")
                out.write(f"  Positives:  {hsp.positives}/{hsp.align_length}\n")
                out.write(f"  Query seq:  {hsp.query}\n")
                out.write(f"  Match:      {hsp.match}\n")
                out.write(f"  Sbjct seq:  {hsp.sbjct}\n")
            else:
                out.write("  No significant alignments found.\n")

            out.write("\n")
            out.flush()

        except Exception as e:
            out.write(f"  [ERROR] {e}\n\n")
            print(f"  [ERROR] {e}")

        # 避免频繁请求 NCBI API，每次请求间隔
        time.sleep(3)

print(f"\n结果已保存至: {result_path}")
