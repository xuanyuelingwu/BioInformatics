
## (5) Genome Browser 可视化展示

为了直观展示 mapping 结果，我们将 BWA 生成的 SAM 文件转换为排序并建索引的 BAM 文件，并使用 **IGV (Integrative Genomics Viewer)** 对酵母基因组（sacCer3）的特定区域进行了可视化。

### 5.1 数据预处理

```bash
# 将 SAM 转换为 BAM，并进行排序和建索引
samtools view -bS THA2-bwa.sam | samtools sort -o THA2-bwa.sorted.bam
samtools index THA2-bwa.sorted.bam

# 下载酵母基因组注释文件并转换为 BED 格式供 IGV 使用
curl -s "https://hgdownload.soe.ucsc.edu/goldenPath/sacCer3/database/sgdGene.txt.gz" -o sgdGene.txt.gz
gunzip -f sgdGene.txt.gz
awk 'BEGIN{OFS="\t"} {print $3, $5, $6, $2, 0, $4, $7, $8, 0, $9, $10, $11}' sgdGene.txt > sgdGene.bed
```

### 5.2 基因区域可视化截图

根据 `samtools depth` 统计，我们在 `chrXII` 染色体上找到了 reads 相对集中的区域，并定位到 **YLL049W** 基因。以下是该区域的 IGV 可视化截图。

**图 1：YLL049W 基因区域总览 (chrXII:39,500-43,000)**
展示了该区域的基因结构（底部黑色粗线为外显子，细线为内含子/UTR）以及 reads 的整体覆盖情况。

![YLL049W Overview](images/YLL049W_overview.png)

**图 2：Reads 详细比对情况 (chrXII:40,500-41,300)**
放大视图展示了单条 reads 的比对细节。图中 reads 按照比对链（Read Strand）着色，粉红色/红色表示比对到正链（Forward strand）。底部轨道展示了参考基因组的碱基序列（Sequence）和氨基酸翻译。

![YLL049W Reads Detail](images/YLL049W_reads_detail.png)
