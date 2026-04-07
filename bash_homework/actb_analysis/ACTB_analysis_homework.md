# ACTB Gene BAM Analysis

**Author:** 鲁奥晗  
**Student ID:** 2023012411

## (1) 单端测序还是双端测序？

**结论：** 提供的 `COAD.ACTB.bam` 文件是**单端测序（Single-end sequencing）**分析的结果。

**原因分析：**
通过检查 BAM 文件的 FLAG 字段，可以发现没有任何一条 read 包含 `0x1`（read paired）标志位。同时，所有 read 的配对相关字段（RNEXT, PNEXT, TLEN）均为空值或 0。

```bash
# 检查是否包含 paired-end FLAG (0x1)
samtools view -f 1 COAD.ACTB.bam | wc -l
# 输出: 0

# 查看前几条记录的 FLAG 值和配对字段
samtools view COAD.ACTB.bam | head -5 | awk '{print "FLAG="$2, "RNEXT="$7, "PNEXT="$8, "TLEN="$9}'
# 输出:
# FLAG=16 RNEXT=* PNEXT=0 TLEN=0
# FLAG=0 RNEXT=* PNEXT=0 TLEN=0
# FLAG=0 RNEXT=* PNEXT=0 TLEN=0
# FLAG=16 RNEXT=* PNEXT=0 TLEN=0
# FLAG=16 RNEXT=* PNEXT=0 TLEN=0
```

## (2) Secondary Alignment 的定义与统计

**Secondary Alignment 定义：**
根据 SAM/BAM 格式官方规范（Sequence Alignment/Map Format Specification v1.6）[1]，当一条 read 由于基因组中的重复序列等原因可以比对到多个位置（Multiple mapping）时，比对软件会选择其中一个作为代表性的 "primary alignment"（通常是最优比对），而该 read 的其余所有比对位置则被标记为 "secondary alignment"。在 SAM 格式中，secondary alignment 通过 FLAG 字段中的 `0x100`（十进制 256）位来标识。

**统计结果：**
在提供的 BAM 文件中，共有 **4,923** 条记录属于 secondary alignment。

```bash
# 统计 secondary alignment 数量 (FLAG 包含 0x100)
samtools view -f 256 COAD.ACTB.bam | wc -l
# 输出: 4923

# 也可以通过 flagstat 查看整体统计
samtools flagstat COAD.ACTB.bam
# 输出片段:
# 185650 + 0 in total (QC-passed reads + QC-failed reads)
# 180727 + 0 primary
# 4923 + 0 secondary
```

## (3) 提取 ACTB 基因 Intron 区域并转换 FASTQ

**步骤 1：计算共有 Intron 区域并输出 BED 格式**
编写 Python 脚本解析 `hg38.ACTB.gff`，提取 ACTB 基因在所有转录本中都被注释为 intron 的区域（即基因区间减去所有转录本 exon 的并集）。

```python
# extract_introns.py 核心逻辑
# 1. 解析 GFF 获取基因区间和所有 exon 区间
# 2. 合并所有重叠的 exon 区间
# 3. 基因区间减去合并后的 exon 区间，得到共有 intron 区间
# 4. 输出为 0-based BED 格式
```

```bash
# 运行脚本提取 intron 区域
python3 extract_introns.py hg38.ACTB.gff ACTB_introns.bed
cat ACTB_introns.bed
# 输出:
# chr7    5528185 5528280 ACTB_intron_1
# chr7    5529982 5530523 ACTB_intron_2
# chr7    5530627 5540675 ACTB_intron_3
# chr7    5540771 5561851 ACTB_intron_4
# chr7    5561949 5562389 ACTB_intron_5
# chr7    5562828 5563713 ACTB_intron_6
```

**步骤 2：提取比对到 Intron 区域的 reads 并转换为 FASTQ**

```bash
# BAM 文件排序并建索引
samtools sort COAD.ACTB.bam -o COAD.ACTB.sorted.bam
samtools index COAD.ACTB.sorted.bam

# 提取比对到 intron 区域的 reads
samtools view -b -L ACTB_introns.bed COAD.ACTB.sorted.bam > COAD.ACTB.intron.bam

# 将 BAM 转换为 FASTQ
samtools fastq COAD.ACTB.intron.bam > COAD.ACTB.intron.fastq

# 统计 FASTQ reads 数量
echo $(( $(wc -l < COAD.ACTB.intron.fastq) / 4 ))
# 输出: 15132
```

## (4) 计算 ACTB 基因区域 Coverage 并输出 BedGraph

使用 `bedtools genomecov` 计算 BAM 文件在 ACTB 基因区间（chr7:5526409-5563902）的覆盖度，并输出为 bedgraph 格式。

```bash
# 计算 coverage 并过滤出 ACTB 基因区域 (BED 格式为 0-based: 5526408-5563902)
bedtools genomecov -ibam COAD.ACTB.sorted.bam -bg | \
  awk '$1=="chr7" && $2>=5526408 && $3<=5563902' > COAD.ACTB.bedgraph

# 查看生成的 bedgraph 文件前 5 行
head -5 COAD.ACTB.bedgraph
# 输出:
# chr7    5527146 5527147 250
# chr7    5527147 5527148 264
# chr7    5527148 5527149 275
# chr7    5527149 5527150 277
# chr7    5527150 5527151 302
```

---

## References
[1] The SAM/BAM Format Specification Working Group. (2024). Sequence Alignment/Map Format Specification. https://samtools.github.io/hts-specs/SAMv1.pdf
