#!/usr/bin/env bash
# ============================================================
# blast_pairwise.sh
# 作者：鲁奥晗  学号：2023012411
#
# 功能：
#   1. 将原始蛋白序列随机打乱，生成10条乱序序列，写入独立的 FASTA 文件
#   2. 对这10条序列两两之间使用本地 blastp 进行比对（共 C(10,2)=45 对）
#      参考：blastp -query seq1.fasta -subject seq2.fasta -out result
#   3. 将所有比对结果汇总输出到 blast_pairwise_results.txt
#
# 依赖：ncbi-blast+（blastp）、Python3
# 安装：sudo apt-get install ncbi-blast+
# ============================================================

set -e  # 遇到错误立即退出

# ---- 原始蛋白序列 ----
ORIGINAL_SEQ="MSTRSVSSSSYRRMFGGPGTASRPSSSRSYVTTSTRTYSLGSALRPSTSRSLYASSPGGVYATRSSAVRL"

# ---- 工作目录（脚本所在目录）----
WORKDIR="$(cd "$(dirname "$0")" && pwd)"
SEQ_DIR="${WORKDIR}/shuffled_seqs"       # 存放10条打乱序列的目录
RESULT_FILE="${WORKDIR}/blast_pairwise_results.txt"

echo "=================================================="
echo "  蛋白序列随机打乱 + 本地两两 blastp 比对脚本"
echo "  原始序列: ${ORIGINAL_SEQ}"
echo "  工作目录: ${WORKDIR}"
echo "=================================================="

# ============================================================
# Step 1: 生成10条随机打乱的序列，每条写入独立的 FASTA 文件
# ============================================================
echo ""
echo "[Step 1] 生成10条随机打乱序列 -> ${SEQ_DIR}/"

mkdir -p "${SEQ_DIR}"

python3 - <<PYEOF
import random, os

original = "${ORIGINAL_SEQ}"
seq_dir  = "${SEQ_DIR}"

random.seed(42)  # 固定随机种子，保证结果可重现

for i in range(1, 11):
    seq_list = list(original)
    random.shuffle(seq_list)          # 随机打乱氨基酸顺序
    shuffled = "".join(seq_list)
    fasta_path = os.path.join(seq_dir, f"seq_{i:02d}.fasta")
    with open(fasta_path, "w") as f:
        f.write(f">shuffled_seq_{i:02d}\n{shuffled}\n")
    print(f"  seq_{i:02d}: {shuffled}")

print(f"\n  已写入 {seq_dir}/seq_01.fasta ~ seq_10.fasta")
PYEOF

# ============================================================
# Step 2: 两两调用本地 blastp 进行比对（共 C(10,2)=45 对）
# ============================================================
echo ""
echo "[Step 2] 开始两两 blastp 比对（共 45 对）..."
echo ""

# 清空/创建结果文件
{
echo "======================================================================"
echo "  蛋白序列两两 blastp 比对结果"
echo "  方法：本地 blastp，-query seq_i.fasta -subject seq_j.fasta"
echo "  参数：-outfmt 0（默认格式），-evalue 10"
echo "======================================================================"
echo ""
} > "${RESULT_FILE}"

PAIR_COUNT=0
TOTAL=45

# 遍历所有 (i, j) 组合，i < j
for i in $(seq 1 10); do
    for j in $(seq $((i+1)) 10); do
        PAIR_COUNT=$((PAIR_COUNT + 1))

        # 格式化序号（补零）
        I_STR=$(printf "%02d" $i)
        J_STR=$(printf "%02d" $j)

        QUERY="${SEQ_DIR}/seq_${I_STR}.fasta"
        SUBJECT="${SEQ_DIR}/seq_${J_STR}.fasta"

        echo "  [${PAIR_COUNT}/${TOTAL}] blastp: shuffled_seq_${I_STR} vs shuffled_seq_${J_STR}"

        # 写入分隔标题
        {
        echo "======================================================================"
        echo "Pair ${PAIR_COUNT}: shuffled_seq_${I_STR} vs shuffled_seq_${J_STR}"
        echo "----------------------------------------------------------------------"
        } >> "${RESULT_FILE}"

        # 调用本地 blastp 进行两序列直接比对
        # -query:   查询序列 FASTA 文件
        # -subject: 目标序列 FASTA 文件（直接两序列比对，无需建库）
        # -evalue:  E-value 阈值（设为 10，保留所有比对结果）
        # -outfmt 0: 默认的 pairwise 格式输出（含比对详情）
        blastp \
            -query   "${QUERY}"   \
            -subject "${SUBJECT}" \
            -evalue  10           \
            -outfmt  0            \
            >> "${RESULT_FILE}" 2>&1

        echo "" >> "${RESULT_FILE}"
    done
done

echo ""
echo "=================================================="
echo "  比对完成！共完成 ${PAIR_COUNT} 对比对。"
echo "  结果文件: ${RESULT_FILE}"
echo "=================================================="
