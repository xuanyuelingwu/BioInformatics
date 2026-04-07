#!/usr/bin/env python3
"""
从GFF文件中提取ACTB基因在每一条转录本中都被注释为intron的区域。

逻辑：对于基因区间内的某个位置，如果它在每一条转录本中都位于intron区域
（即不属于该转录本的任何exon），则该位置属于"共有intron"。

实现方式：
1. 获取基因区间 [gene_start, gene_end]
2. 对每条转录本，计算其intron区域 = 转录本区间 - exon区域
3. 取所有转录本intron区域的交集

注意：只有落在某条转录本范围内的位置，才能被该转录本定义为intron。
如果某个位置不在某条转录本的范围内，则该转录本对此位置没有定义。
因此，"在每一条转录本中都是intron"意味着：该位置在每一条覆盖它的转录本中都是intron。

但更严格的理解是：该位置必须在所有转录本的范围内，且在所有转录本中都是intron。
这里采用更合理的理解：该位置在所有转录本中都不被注释为exon，
即 gene_interval - union(all_exons_from_all_transcripts)。
"""

import sys
from collections import defaultdict

gff_file = sys.argv[1]
output_bed = sys.argv[2]

transcripts = defaultdict(list)
transcript_ranges = {}
gene_chrom = None
gene_start = None
gene_end = None
gene_strand = None

with open(gff_file) as f:
    for line in f:
        if line.startswith('#'):
            continue
        fields = line.strip().split('\t')
        if len(fields) < 9:
            continue
        chrom, source, feature, start, end, score, strand, frame, attrs = fields
        start, end = int(start), int(end)

        if feature == 'gene':
            gene_chrom = chrom
            gene_start = start
            gene_end = end
            gene_strand = strand

        if feature == 'transcript':
            for attr in attrs.split(';'):
                if attr.strip().startswith('transcript_id='):
                    tid = attr.strip().split('=')[1]
                    transcript_ranges[tid] = (start, end)
                    break

        if feature == 'exon':
            for attr in attrs.split(';'):
                if attr.strip().startswith('transcript_id='):
                    tid = attr.strip().split('=')[1]
                    transcripts[tid].append((start, end))
                    break

print(f"基因区间: {gene_chrom}:{gene_start}-{gene_end} ({gene_strand})")
print(f"共 {len(transcripts)} 条转录本\n")

# 收集所有exon区域并合并
all_exons = []
for tid, exons in transcripts.items():
    all_exons.extend(exons)

# 合并重叠的exon区域
all_exons.sort()
merged_exons = []
for start, end in all_exons:
    if merged_exons and start <= merged_exons[-1][1] + 1:
        merged_exons[-1] = (merged_exons[-1][0], max(merged_exons[-1][1], end))
    else:
        merged_exons.append((start, end))

print(f"合并后的exon区域: {len(merged_exons)} 个")
for s, e in merged_exons:
    print(f"  {gene_chrom}:{s}-{e} ({e-s+1} bp)")

# 基因区间减去所有exon的并集 = 共有intron区域
introns = []
prev_end = gene_start - 1  # 基因起始之前
for exon_start, exon_end in merged_exons:
    if exon_start > prev_end + 1:
        intron_start = prev_end + 1
        intron_end = exon_start - 1
        introns.append((intron_start, intron_end))
    prev_end = max(prev_end, exon_end)

# 检查基因末尾是否有intron
if prev_end < gene_end:
    introns.append((prev_end + 1, gene_end))

print(f"\n在所有转录本中都是intron的区域: {len(introns)} 个")

with open(output_bed, 'w') as out:
    for i, (start, end) in enumerate(introns):
        # GFF 1-based inclusive -> BED 0-based half-open
        bed_start = start - 1
        bed_end = end
        out.write(f"{gene_chrom}\t{bed_start}\t{bed_end}\tACTB_intron_{i+1}\n")
        print(f"  {gene_chrom}:{bed_start}-{bed_end} (ACTB_intron_{i+1}, {bed_end-bed_start} bp)")

total_intron_bp = sum(e - s for s, e in [(start-1, end) for start, end in introns])
print(f"\n共有intron总长度: {total_intron_bp} bp")
print(f"结果已输出到 {output_bed}")
