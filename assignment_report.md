# 生物信息学作业报告

**作者**：鲁奥晗**学号**：2023012411

---

## 1. 网页版 blastp 比对及 E-value/P-value 解释

### 1.1 操作过程与结果截图

**操作步骤**：

1. 打开 NCBI BLAST 网页，选择 **blastp**（Protein BLAST）。

1. 在 **Enter Query Sequence** 框中输入给定的蛋白序列：`MSTRSVSSSSYRRMFGGPGTASRPSSSRSYVTTSTRTYSLGSALRPSTSRSLYASSPGGVYATRSSAVRL`。

1. 在 **Choose Search Set** 区域，将 **Organism** 限定为 `Mus musculus (taxid:10090)`。

1. 展开 **Algorithm parameters**，将 **Max target sequences** 设置为 `10`，将 **Expect threshold**（E 值）设置为 `0.5`。

1. 点击 **BLAST** 按钮提交查询。

**操作过程截图**：![BLASTP 参数设置](https://private-us-east-1.manuscdn.com/sessionFile/zbYPreruhXwvnirazspazl/sandbox/ixpL1Z4DkMa9K6MTIqUmrG-images_1773762259254_na1fn_L2hvbWUvdWJ1bnR1L0Jpb0luZm9ybWF0aWNzL2JsYXN0cF9zZXR0aW5nc19mdWxs.webp?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvemJZUHJlcnVoWHd2bmlyYXpzcGF6bC9zYW5kYm94L2l4cEwxWjREa01hOUs2TVRJcVVtckctaW1hZ2VzXzE3NzM3NjIyNTkyNTRfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwwSnBiMGx1Wm05eWJXRjBhV056TDJKc1lYTjBjRjl6WlhSMGFXNW5jMTltZFd4cy53ZWJwIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzk4NzYxNjAwfX19XX0_&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=Z0wnwvQb2EFtiNgo0ok2DikNvJ17JuMg3h7a0Vu73J0ULWrrQSoCEtKrm45J2c3EkZQy6Lg3q3Y4w9BMgr1v5-9P~JmqCrSNK6hA2X92jddZ2T8OOr-xkk-T9PDEsewWN4qsh4kfuY5Vqw8I-Rr9m3CYiaDzuS44C5wobclU-lufSztT0h4YN2dR00g1~GyTdVj5d4uBIIrLubp5yi0nVK6GqK7uN5MtIucq-bDPI4nSdfoS4sdhBCliD6OalQLjGC0O9XAUOzHjj7QSF1vZKYQqCKIOnnimGLEHkgZtGlxsNh7bx1ZTp0Bv3G-NuvsCB43zwmNQpR3ilPLnNHccKw__)

**比对结果截图**：![BLASTP 结果列表](https://private-us-east-1.manuscdn.com/sessionFile/zbYPreruhXwvnirazspazl/sandbox/ixpL1Z4DkMa9K6MTIqUmrG-images_1773762259254_na1fn_L2hvbWUvdWJ1bnR1L0Jpb0luZm9ybWF0aWNzL2JsYXN0cF90cmFkaXRpb25hbF9yZXN1bHRz.webp?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvemJZUHJlcnVoWHd2bmlyYXpzcGF6bC9zYW5kYm94L2l4cEwxWjREa01hOUs2TVRJcVVtckctaW1hZ2VzXzE3NzM3NjIyNTkyNTRfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwwSnBiMGx1Wm05eWJXRjBhV056TDJKc1lYTjBjRjkwY21Ga2FYUnBiMjVoYkY5eVpYTjFiSFJ6LndlYnAiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=sEXzcCfjEZesghKDC9BGs65KX0VAbAOToLvJoaYn6ZP4dx2xFCLUtnm05bAZQjzUsZSzDDO-TJ3uZtGHFD2uK9~1h5QnEs6YK7J4vqK41q~0wBaX~KEChdAUPwHtRlqrkZxczaMXWX276awNN7r1uwxYc1J6dWFamGIYvAid434ryh7kNpzh5R5eI34v3BmkAqNA0EMbH2sM7YHpMVFr5wIKN7L7-4pqgUYXxlwIUxKERPtr3hUDKH7nAI~ytYf~~6MSKxP9-RS6QPVtFHruLStKcEA-QEvk-VjfEAvWYLh23JOPYakIUlRhrGelKf9ERZSqAqoIOjfBMNoBbXsyAA__)![BLASTP 比对详情](https://private-us-east-1.manuscdn.com/sessionFile/zbYPreruhXwvnirazspazl/sandbox/ixpL1Z4DkMa9K6MTIqUmrG-images_1773762259254_na1fn_L2hvbWUvdWJ1bnR1L0Jpb0luZm9ybWF0aWNzL2JsYXN0cF9hbGlnbm1lbnRz.webp?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvemJZUHJlcnVoWHd2bmlyYXpzcGF6bC9zYW5kYm94L2l4cEwxWjREa01hOUs2TVRJcVVtckctaW1hZ2VzXzE3NzM3NjIyNTkyNTRfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwwSnBiMGx1Wm05eWJXRjBhV056TDJKc1lYTjBjRjloYkdsbmJtMWxiblJ6LndlYnAiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=NTdQODSLbGwfezDlEWNyuo~1~oivRkgrwngTLBRZjA~oOBU42U8ilYlrbOBzV7uqT98AFxegB-FZ7lBl~W8wU1jB4YpHceNnZoLuz0C5IodTROrpqXTCN2AIW44pBZPzNQ7I5~Jc8IIn4Ws1TvSSVaQiZDHXT9~RCcXZjUns3lTNBtkn8d~SDuX013sNHOOJpn2eIT3N9LzcC8xFBICA~56FOJUznEaZrF58SAdduEk2Tqjn8mtspKIyxb415rI2EqkD26jX2zBZfN0FuK7Bd2ROcHPOj9l3-9wXtJedv3II9kSLEIcNUxk-slM4BtaDF4VnwwpyHIWT1d3xs23HCQ__)

### 1.2 E-value 和 P-value 的实际意义

| 指标 | 全称 | 实际意义 |
| --- | --- | --- |
| **E-value** | Expectation value (期望值) | 表示在当前大小的数据库中，**完全由随机偶然性**产生与当前比对得分相同或更高得分的比对结果的**期望次数**。E-value 越接近 0，说明比对结果越不可能是随机产生的，即两条序列具有真实的同源性。例如，E-value = 0.01 意味着在当前数据库中随机搜索，预期会找到 0.01 个这样高分的匹配。 |
| **P-value** | Probability value (概率值) | 表示在随机情况下，观察到至少一个得分等于或高于当前比对得分的**概率**。P-value 的取值范围是 [0] [1]。P-value 越小，说明比对结果是随机事件的概率越低，结果越显著。 |

**两者关系**：E-value 和 P-value 之间存在数学关系：`P = 1 - e^{-E}`。当 E-value 很小（如 E < 0.01）时，P-value 约等于 E-value。在 BLAST 结果中，通常使用 E-value 来衡量比对的显著性，因为它更直观地反映了在特定数据库大小下的假阳性预期数量。

---

## 2. Bash 脚本：随机打乱序列并两两比对

### 2.1 脚本代码与注释

为了完成序列的随机打乱和两两比对，我编写了 `blast_pairwise.sh` 脚本。该脚本内嵌了 Python 代码来处理序列打乱并生成独立的 FASTA 文件，然后使用本地安装的 `ncbi-blast+` 工具（`blastp`）直接进行两两序列比对（无需建库）。

```bash
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

ORIGINAL_SEQ="MSTRSVSSSSYRRMFGGPGTASRPSSSRSYVTTSTRTYSLGSALRPSTSRSLYASSPGGVYATRSSAVRL"
WORKDIR="$(cd "$(dirname "$0")" && pwd)"
SEQ_DIR="${WORKDIR}/shuffled_seqs"
RESULT_FILE="${WORKDIR}/blast_pairwise_results.txt"

# Step 1: 生成10条随机打乱的序列，每条写入独立的 FASTA 文件
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
PYEOF

# Step 2: 两两调用本地 blastp 进行比对（共 C(10,2)=45 对）
{
echo "======================================================================"
echo "  蛋白序列两两 blastp 比对结果"
echo "  方法：本地 blastp，-query seq_i.fasta -subject seq_j.fasta"
echo "  参数：-outfmt 0（默认格式），-evalue 10"
echo "======================================================================"
echo ""
} > "${RESULT_FILE}"

PAIR_COUNT=0

# 遍历所有 (i, j) 组合，i < j
for i in $(seq 1 10); do
    for j in $(seq $((i+1)) 10); do
        PAIR_COUNT=$((PAIR_COUNT + 1))
        I_STR=$(printf "%02d" $i)
        J_STR=$(printf "%02d" $j)

        QUERY="${SEQ_DIR}/seq_${I_STR}.fasta"
        SUBJECT="${SEQ_DIR}/seq_${J_STR}.fasta"

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
```

### 2.2 结果示例与解释

在 45 对比对中，有 16 对结果为 `***** No hits found *****`，其余 29 对找到了局部匹配。以下是 `blast_pairwise_results.txt` 中有命中的部分结果示例：

```text
======================================================================
Pair 2: shuffled_seq_01 vs shuffled_seq_03
----------------------------------------------------------------------
...
Query= shuffled_seq_01
Length=70
                                                                      Score     E
Sequences producing significant alignments:                          (Bits)  Value
shuffled_seq_03                                                        9.2    8.9  

> shuffled_seq_03
Length=70

 Score =  9.2 bits (12),  Expect = 8.9, Method: Compositional matrix adjust.
 Identities = 4/6 (67%), Positives = 5/6 (83%), Gaps = 0/6 (0%)

Query  11  SGSATS  16
           +GSA S
Sbjct  48  TGSARS  53
```

**结果解释**：
由于这 10 条序列都是由同一条原始序列随机打乱生成的，它们的氨基酸组成（Composition）完全相同，但序列顺序（Order）被破坏。

1. **极低的得分与极高的 E-value**：
   在找到的匹配中，得分（Score）普遍极低（通常在 9.2 到 20.8 bits 之间），且 E-value 极大（如 8.9、1.1 等，远大于通常认为显著的 0.05 阈值）。这说明它们之间**没有显著的进化同源性**。
   
2. **短小的局部匹配**：
   `blastp` 找到的匹配区域非常短（通常只有 6 到 20 个氨基酸长度），这主要是由于原始序列中富含丝氨酸（S）、精氨酸（R）和苏氨酸（T）等残基，随机打乱后偶然形成了短的相似片段。

3. **大量无匹配（No hits found）**：
   有超过三分之一（16/45）的序列对连这种短小的随机匹配都找不到，直接返回 `No hits found`。这进一步证明了仅仅氨基酸组成相同，并不足以在 BLAST 搜索中产生有意义的比对结果，序列的**排列顺序**才是决定蛋白质结构和同源性的关键。

---

## 3. BLAST 提高速度的方法及原理

除了动态规划（Dynamic Programming，如 Smith-Waterman 算法），BLAST（Basic Local Alignment Search Tool）主要利用了**启发式算法（Heuristic Algorithm）**来大幅提高搜索速度。其核心思想是**“种子与延伸”（Seed-and-Extend）**策略。

### 3.1 核心加速方法

1. **词语查找（Word Lookup / K-mer Hashing）**：BLAST 首先将查询序列分割成长度为 $W$ 的短片段（称为 Word 或 K-mer，蛋白质通常 $W=3$）。然后，它在数据库中快速扫描这些短片段的精确匹配或高分匹配（使用替换矩阵如 BLOSUM62 评估得分高于阈值 $T$ 的词）。这一步通过预先构建的**哈希表（Hash Table）**或有限状态自动机实现，查找速度极快。

1. **双击触发（Two-Hit Trigger）**：为了减少假阳性延伸，现代 BLAST 算法要求在同一条对角线上、距离在一定范围（$A$）内找到**两个**不重叠的 Word 匹配（Hits），才会触发后续的延伸步骤。

1. **无空位与有空位延伸（Ungapped and Gapped Extension）**：只有当找到符合条件的“种子”后，BLAST 才会向两端进行延伸。首先进行快速的无空位延伸，如果得分超过某个阈值，再进行耗时的有空位延伸（此时才局部使用动态规划）。

### 3.2 为什么可以提高速度？

动态规划算法（如 Smith-Waterman）需要计算一个 $M \times N$ 的矩阵（$M$ 为查询序列长度，$N$ 为数据库总长度），时间复杂度为 $O(MN)$。对于庞大的现代数据库，这是不可接受的。

BLAST 的启发式方法之所以快，是因为它**极大地缩小了搜索空间**。它假设：**如果两条序列具有显著的同源性，那么它们之间必然共享至少一小段高度相似的区域（即 Word Hit）**。

- 通过哈希表快速定位这些“种子”，BLAST 过滤掉了数据库中 99% 以上完全不相关的序列，避免了对它们进行无意义的动态规划计算。

- 只有在极少数有潜力的候选区域，BLAST 才投入计算资源进行延伸和动态规划。

- 这种策略用极小的敏感度（Sensitivity）损失，换取了成百上千倍的速度提升。

---

## 4. PAM250 矩阵的对称与不对称性分析

PAM（Point Accepted Mutation）矩阵是基于已知进化树中密切相关的蛋白质序列的突变频率构建的。

### 4.1 对称与不对称 PAM 矩阵的区别原因

1. **不对称的突变概率矩阵（Mutation Probability Matrix, $M$）**：
   在实际的生物进化中，氨基酸 $i$ 突变为氨基酸 $j$ 的概率，与氨基酸 $j$ 突变为氨基酸 $i$ 的概率是**不相等**的。这取决于两种氨基酸在自然界中的背景频率（丰度）以及它们的化学性质。例如，一种罕见的氨基酸突变为一种常见的氨基酸的概率，通常大于常见氨基酸突变为罕见氨基酸的概率。因此，原始的突变概率矩阵 $M$ 是**不对称**的。

2. **对称的替换打分矩阵（Substitution Scoring Matrix, PAM）**：
   我们在序列比对中实际使用的 PAM 矩阵（如 PAM250），其矩阵元素（打分值）是对称的（即 $S_{ij} = S_{ji}$）。
   根据 Wikipedia 的解释 [1]，这种对称性源于突变概率矩阵的一个重要关系式：
   $$ f(j)M(i,j) = f(i)M(j,i) $$
   其中 $f(j)$ 是氨基酸 $j$ 的背景频率，$M(i,j)$ 是氨基酸 $j$ 突变为氨基酸 $i$ 的概率。这个关系式表明，在平衡状态下，从 $j$ 突变为 $i$ 的总期望次数等于从 $i$ 突变为 $j$ 的总期望次数。
   
   这个关系对于矩阵 $M$ 的任意正整数次幂 $n$ 同样成立：
   $$ f(j)M^n(i,j) = f(i)M^n(j,i) $$
   
   在构建 $\text{PAM}_n$ 打分矩阵时，矩阵元素定义为对数比值（Log-odds ratio）：
   $$ \text{PAM}_n(i,j) = \log \frac{f(j)M^n(i,j)}{f(j)f(i)} $$
   
   利用上述关系式，我们可以推导出 $\text{PAM}_n$ 矩阵的对称性：
   $$ \text{PAM}_n(i,j) = \log \frac{f(j)M^n(i,j)}{f(j)f(i)} = \log \frac{f(i)M^n(j,i)}{f(i)f(j)} = \text{PAM}_n(j,i) $$
   
   因此，尽管底层的突变概率矩阵 $M$ 是不对称的，但基于对数比值构建的 $\text{PAM}_n$ 打分矩阵必然是**对称**的。

![PAM 矩阵对称性推导](pam_symmetry_proof.webp)

### 4.2 在应用上的不同

| 矩阵类型 | 特点 | 应用场景 |
| --- | --- | --- |
| **不对称矩阵** (突变概率矩阵 $M$) | 反映了进化的方向性和氨基酸的背景频率差异。$M_{ij} \neq M_{ji}$。 | 主要用于**进化生物学**和**系统发生学**。例如：构建系统发育树、模拟蛋白质的进化过程、计算序列在特定进化时间下的期望状态。 |
| **对称矩阵** (打分矩阵 PAM250) | 忽略了进化方向，基于对数比值构建。$S_{ij} = S_{ji}$。 | 主要用于**序列比对**（如 BLAST、Smith-Waterman）。在比对两条未知祖先的序列时，对称矩阵能够公平地评估 $i$ 匹配 $j$ 和 $j$ 匹配 $i$ 的得分，是数据库搜索和同源性推断的标准工具。 |

> "While the mutation probability matrix $M$ is not symmetric, each of the PAM matrices are. This somewhat surprising property is a result of the relationship that was noted for the mutation probability matrix: $f(j)M(i,j) = f(i)M(j,i)$." [1]

---

## 参考文献

[1]: https://en.wikipedia.org/wiki/Point_accepted_mutation "Wikipedia. "Point accepted mutation"."

