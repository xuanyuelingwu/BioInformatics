# Mapping Homework

**Author:** 鲁奥晗  
**Student ID:** 2023012411

## (1) Bowtie中BWT的性质与内存优化策略

### BWT的性质提高运算速度
Bowtie利用了Burrows-Wheeler Transform (BWT) 的**LF-mapping（Last-to-First mapping）性质**和**Backward Search（逆向搜索）算法**来极大提高比对速度。LF-mapping指出，BWT矩阵最后一列（L列）中某字符的第$i$次出现，与第一列（F列）中该字符的第$i$次出现，对应于原始序列中的同一个字符。基于此性质，Backward Search算法允许从待比对序列（read）的最后一个字符开始，从右向左逐个字符进行精确匹配。在每一步匹配中，算法通过查询预先计算好的数组，可以在$O(1)$时间内确定前缀在后缀数组中的区间范围。因此，精确匹配一个长度为$m$的read的时间复杂度仅为$O(m)$，完全独立于参考基因组的大小，从而实现了超快的比对速度。

### 内存优化策略
为了在普通计算机上运行人类基因组级别的比对，Bowtie采用了基于FM-index的内存优化策略，主要包括：
1. **Occ表（Occurrence Array）检查点采样**：完整存储Occ表（记录每个字符在L列前$i$个位置的出现次数）需要消耗大量内存。Bowtie通过仅在每隔一定行数（如每32行或128行）存储一个检查点（Checkpoint）来压缩内存。查询非检查点行时，只需从最近的检查点出发，扫描L列中相邻的几个字符即可计算出结果，从而在查询时间略微增加的情况下大幅降低了内存占用。
2. **后缀数组（Suffix Array, SA）采样**：完整的后缀数组需要为基因组的每个位置存储一个指针。Bowtie对SA进行等距采样（例如每隔32个位置存储一个值）。当比对完成后需要将BWT索引位置转换为基因组实际坐标时，如果当前位置未被采样，算法会利用LF-mapping在BWT中不断向前回溯，直到遇到一个被采样的位置，再加上回溯的步数即可得到实际坐标。
3. **双位编码与压缩**：DNA序列仅包含A、C、G、T四种碱基，Bowtie使用2-bit编码来表示每个碱基，并利用BWT转换后相同字符容易聚集的特性，进一步提高了数据的压缩率。

## (2) Bowtie Mapping与各染色体Reads统计

```bash
# 执行Bowtie mapping
bowtie -v 2 -m 10 --best --strata BowtieIndex/YeastGenome -f THA2.fa -S THA2.sam

# 统计mapping到不同染色体上的reads数量
samtools view -F 4 THA2.sam | awk '{print $3}' | sort | uniq -c | sort -rn
```

```text
    194 Scchr04
    169 Scchr12
    125 Scchr07
    101 Scchr15
     78 Scchr16
     71 Scchr10
     68 Scchr08
     67 Scchr13
     58 Scchr14
     56 Scchr11
     51 Scchr02
     33 Scchr05
     25 Scchr09
     18 Scchr01
     17 Scchr06
     15 Scchr03
     12 Scmito
```

## (3) SAM/BAM文件格式问题

### (3.1) CIGAR string的含义与信息
CIGAR (Compact Idiosyncratic Gapped Alignment Report) string 是SAM/BAM文件中用于描述read与参考基因组比对详细情况的字符串。它由数字和字母（操作符）交替组成，例如`36M`、`10M2I24M`等。数字代表碱基的数量，字母代表比对的状态。它包含了read在比对区域内哪些碱基是匹配/错配的（M）、哪些是插入（I）、哪些是缺失（D）、哪些被剪切（S或H）等详细的碱基级别比对结构信息。

### (3.2) Soft clip的含义与表示
"Soft clip"（软剪切）表示read的某一部分序列未能与参考基因组成功比对，但这段未比对上的序列仍然被保留在SAM/BAM文件的SEQ字段中。这通常发生在read的边缘，可能是由于测序接头污染、低质量碱基或结构变异导致的。在CIGAR string中，soft clip用字母**S**表示，例如`5S31M`表示read的前5个碱基被软剪切，随后的31个碱基成功比对。

### (3.3) Mapping quality的含义与信息
Mapping quality（MAPQ，比对质量值）是一个数值（通常为0-255），反映了比对软件对该read比对到参考基因组特定位置的置信度。它在数学上定义为 $-10 \times \log_{10}(P)$，其中$P$是该比对位置是错误的概率。MAPQ值越高，表示比对结果越可靠。它综合反映了read的唯一性（是否多重比对）、错配数量、测序质量等信息。如果一个read能以相似的得分比对到基因组的多个位置，其MAPQ值通常会被设为0或非常低的值。

### (3.4) 仅根据SAM/BAM推断参考基因组序列
仅根据SAM/BAM文件中的信息**不能**完全推断出read mapping到的区域对应的参考基因组序列。虽然SAM文件包含了read的序列（SEQ）和比对情况（CIGAR），并且可以通过MD标签（如果存在）得知错配和缺失的具体碱基，但对于read中发生插入（Insertion, I）的区域，参考基因组在对应位置是没有碱基的；而对于参考基因组中发生缺失（Deletion, D）的区域，SAM文件通常只记录了缺失的长度，而不包含缺失的具体碱基序列。因此，要获得完整的参考基因组序列，必须依赖原始的FASTA参考文件。

## (4) BWA安装与Yeast基因组Mapping

```bash
# 安装BWA
sudo apt-get install -y bwa

# 对Yeast基因组建立索引
bwa index sacCer3.fa

# 使用BWA将THA2.fa比对到Yeast参考基因组
# 由于THA2.fa包含较短的reads，使用bwa aln/samse流程
bwa aln sacCer3.fa THA2.fa > THA2-bwa.sai
bwa samse sacCer3.fa THA2-bwa.sai THA2.fa > THA2-bwa.sam

# 统计BWA mapping结果
samtools view -F 4 THA2-bwa.sam | awk '{print $3}' | sort | uniq -c | sort -rn
```

```text
    202 chrIV
    178 chrXII
    129 chrVII
    108 chrXV
     83 chrXVI
     77 chrX
     72 chrXIII
     70 chrVIII
     60 chrXI
     59 chrXIV
     54 chrII
     38 chrV
     26 chrIX
     18 chrVI
     18 chrM
     17 chrIII
     17 chrI
```
