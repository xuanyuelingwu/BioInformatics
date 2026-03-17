# Bash 脚本作业报告

**作者**：鲁奥晗  
**学号**：2023012411

## 1. Bash 脚本代码 (`list_contents.sh`)

```bash
#!/bin/bash
# =============================================================================
# 脚本名称：list_contents.sh
# 功    能：读取指定文件夹的直接内容，将文件名写入 filenames.txt，
#           将子文件夹名写入 dirname.txt，输出文件保存在脚本所在目录。
# 用    法：bash list_contents.sh [目标文件夹路径]
#           若不提供参数，则默认读取 bash_homework/ 目录。
# =============================================================================

# 1. 确定目标文件夹
TARGET_DIR="${1:-bash_homework/}"

# 2. 检查目标文件夹是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "错误：目录 '$TARGET_DIR' 不存在，请检查路径后重试。" >&2
    exit 1
fi

# 3. 确定输出文件的保存路径
SCRIPT_DIR="$(dirname "$0")"
FILENAMES_OUT="${SCRIPT_DIR}/filenames.txt"
DIRNAME_OUT="${SCRIPT_DIR}/dirname.txt"

# 4. 清空（或新建）输出文件
> "$FILENAMES_OUT"
> "$DIRNAME_OUT"

# 5. 遍历目标文件夹下的直接内容
for item in "$TARGET_DIR"/*; do
    [ -e "$item" ] || continue
    name="$(basename "$item")"

    if [ -f "$item" ]; then
        echo "$name" >> "$FILENAMES_OUT"
    elif [ -d "$item" ]; then
        echo "$name" >> "$DIRNAME_OUT"
    fi
done

# 6. 统计并打印结果摘要
FILE_COUNT=$(wc -l < "$FILENAMES_OUT")
DIR_COUNT=$(wc -l < "$DIRNAME_OUT")

echo "========================================"
echo "  目标文件夹：$TARGET_DIR"
echo "  文件数量  ：$FILE_COUNT 个 → 已写入 $FILENAMES_OUT"
echo "  子目录数量：$DIR_COUNT 个 → 已写入 $DIRNAME_OUT"
echo "========================================"
```

## 2. 运行结果输出

### 2.1 终端输出

```text
========================================
  目标文件夹：bash_homework/
  文件数量  ：30 个 → 已写入 ./filenames.txt
  子目录数量：40 个 → 已写入 ./dirname.txt
========================================
```

### 2.2 `filenames.txt` 内容

```text
a.txt
a1.txt
b.filter_random.pl
b1.txt
bam_wig.sh
c.txt
c1.txt
chrom.size
d1.txt
data.csv
dir.txt
e1.txt
f1.txt
file1.txt
file2.sh
human_geneExp.txt
if.sh
image
insitiue.txt
mouse_geneExp.txt
name.txt
number.sh
out.bw
random.sh
read.sh
test.sh
test.txt
test3.sh
test4.sh
wigToBigWig
```

### 2.3 `dirname.txt` 内容

```text
RBP_map
a-docker
app
backup
bin
biosoft
c1-RBPanno
datatable
db
download
e-annotation
exRNA
genome
git
highcharts
home
hub29
ibme
l-lwl
map2
mljs
module
mogproject
node_modules
perl5
postar.docker
postar2
postar_app
rout
script
script_backup
software
subdir1
subdir2
tcga
test
tmp
tmp_script
var
x-rbp
```
