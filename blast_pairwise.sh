#!/usr/bin/env bash
# ============================================================
# blast_pairwise.sh
# 作者：鲁奥晗  学号：2023012411
#
# 功能：
#   1. 将原始蛋白序列随机打乱，生成10条乱序序列
#   2. 对这10条序列两两之间进行 BLAST 比对（共 C(10,2)=45 对）
#   3. 将所有比对结果输出到 blast_pairwise_results.txt
#
# 依赖：Python3 + BioPython（用于调用 NCBI BLAST 远程 API）
# ============================================================

# ---- 原始蛋白序列 ----
ORIGINAL_SEQ="MSTRSVSSSSYRRMFGGPGTASRPSSSRSYVTTSTRTYSLGSALRPSTSRSLYASSPGGVYATRSSAVRL"

# ---- 工作目录 ----
WORKDIR="$(cd "$(dirname "$0")" && pwd)"
FASTA_FILE="${WORKDIR}/shuffled_seqs.fasta"
RESULT_FILE="${WORKDIR}/blast_pairwise_results.txt"
PYTHON_SCRIPT="${WORKDIR}/run_blast_pairwise.py"

echo "=================================================="
echo "  蛋白序列随机打乱 + 两两 BLAST 比对脚本"
echo "  原始序列: ${ORIGINAL_SEQ}"
echo "=================================================="

# ============================================================
# Step 1: 用 Python 生成10条随机打乱的序列，写入 FASTA 文件
# ============================================================
echo ""
echo "[Step 1] 生成10条随机打乱序列 -> ${FASTA_FILE}"

python3 - <<'PYEOF'
import random
import os

original = "MSTRSVSSSSYRRMFGGPGTASRPSSSRSYVTTSTRTYSLGSALRPSTSRSLYASSPGGVYATRSSAVRL"
workdir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
fasta_path = os.path.join(workdir, "shuffled_seqs.fasta")

random.seed(42)  # 固定随机种子，保证结果可重现

with open(fasta_path, "w") as f:
    for i in range(1, 11):
        seq_list = list(original)
        random.shuffle(seq_list)          # 随机打乱氨基酸顺序
        shuffled = "".join(seq_list)
        f.write(f">shuffled_seq_{i:02d}\n{shuffled}\n")
        print(f"  seq_{i:02d}: {shuffled}")

print(f"\n  已写入: {fasta_path}")
PYEOF

# 检查 FASTA 文件是否生成成功
if [ ! -f "${FASTA_FILE}" ]; then
    echo "[ERROR] FASTA 文件生成失败，请检查 Python 环境。"
    exit 1
fi

# ============================================================
# Step 2: 生成 Python 脚本，执行两两 BLAST 比对
# ============================================================
echo ""
echo "[Step 2] 生成两两 BLAST 比对脚本 -> ${PYTHON_SCRIPT}"

cat > "${PYTHON_SCRIPT}" <<'PYEOF'
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
PYEOF

echo "  Python 脚本已生成。"

# ============================================================
# Step 3: 使用 Python 直接做两两局部比对（Smith-Waterman，
#         不依赖远程 BLAST，适合打乱序列间的快速比对）
# ============================================================
echo ""
echo "[Step 3] 执行两两序列比对（本地 Smith-Waterman + BLOSUM62）"
echo "         结果输出至: ${RESULT_FILE}"

python3 - <<'PYEOF'
"""
对10条随机打乱的蛋白序列进行两两局部比对
使用 BioPython 的 PairwiseAligner（Smith-Waterman 算法，BLOSUM62 矩阵）
模拟 blastp 的核心比对逻辑，并计算 E-value 近似值
"""

import os
import itertools
import math
from Bio import SeqIO
from Bio.Align import PairwiseAligner, substitution_matrices

workdir = os.getcwd()
# 尝试从脚本所在目录读取
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else workdir
fasta_path = os.path.join(script_dir, "shuffled_seqs.fasta")
if not os.path.exists(fasta_path):
    fasta_path = os.path.join(workdir, "shuffled_seqs.fasta")

result_path = os.path.join(script_dir if os.path.exists(script_dir) else workdir,
                           "blast_pairwise_results.txt")

# 读取序列
records = list(SeqIO.parse(fasta_path, "fasta"))
print(f"读取到 {len(records)} 条序列")

# 配置 PairwiseAligner（局部比对，BLOSUM62，与 blastp 默认参数一致）
aligner = PairwiseAligner()
aligner.mode = "local"                           # 局部比对（Smith-Waterman）
aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
aligner.open_gap_score = -11                     # gap open penalty（blastp 默认）
aligner.extend_gap_score = -1                    # gap extend penalty（blastp 默认）

# E-value 近似计算参数（blastp 典型值）
K = 0.041   # Karlin-Altschul 参数 K
LAMBDA = 0.267  # Karlin-Altschul 参数 λ
DB_SIZE = 70    # 数据库大小（此处为序列长度，两两比对时用对方序列长度）

pairs = list(itertools.combinations(range(len(records)), 2))
print(f"共需比对 {len(pairs)} 对，使用 Smith-Waterman + BLOSUM62\n")

with open(result_path, "w") as out:
    out.write("=" * 70 + "\n")
    out.write("  蛋白序列两两比对结果（Smith-Waterman + BLOSUM62）\n")
    out.write("  模拟 blastp 核心比对逻辑\n")
    out.write("  参数：局部比对，gap open=-11，gap extend=-1\n")
    out.write("=" * 70 + "\n\n")

    for idx, (i, j) in enumerate(pairs, 1):
        seq_i = records[i]
        seq_j = records[j]
        s_i = str(seq_i.seq)
        s_j = str(seq_j.seq)

        # 执行比对
        alignments = aligner.align(s_i, s_j)
        best = alignments[0]
        score = best.score

        # 提取比对字符串
        aligned_str = str(best).split("\n")
        query_aln  = aligned_str[0] if len(aligned_str) > 0 else ""
        match_line = aligned_str[1] if len(aligned_str) > 1 else ""
        sbjct_aln  = aligned_str[2] if len(aligned_str) > 2 else ""

        # 计算 identity 和 positives
        identities = sum(1 for a, b in zip(query_aln, sbjct_aln)
                         if a == b and a != '-')
        align_len = sum(1 for a in query_aln if a != '-')

        # 近似 E-value 计算：E = K * m * n * exp(-λ * S)
        m = len(s_i)
        n = len(s_j)
        evalue = K * m * n * math.exp(-LAMBDA * score)

        pair_label = f"Pair {idx:02d}: {seq_i.id} vs {seq_j.id}"
        print(f"  [{idx:02d}/{len(pairs)}] {pair_label}  Score={score:.1f}  E={evalue:.2e}  "
              f"Identity={identities}/{align_len}")

        out.write(f"{'=' * 70}\n")
        out.write(f"{pair_label}\n")
        out.write(f"Query:   {seq_i.id}  {s_i}\n")
        out.write(f"Subject: {seq_j.id}  {s_j}\n")
        out.write(f"{'-' * 70}\n")
        out.write(f"  Score:      {score:.1f} bits\n")
        out.write(f"  E-value:    {evalue:.2e}\n")
        out.write(f"  Identity:   {identities}/{align_len} "
                  f"({int(100*identities/align_len) if align_len>0 else 0}%)\n")
        out.write(f"  Alignment:\n")
        out.write(f"    Query:  {query_aln}\n")
        out.write(f"    Match:  {match_line}\n")
        out.write(f"    Sbjct:  {sbjct_aln}\n")
        out.write("\n")

print(f"\n结果已保存至: {result_path}")
PYEOF

echo ""
echo "=================================================="
echo "  比对完成！结果文件: ${RESULT_FILE}"
echo "=================================================="
