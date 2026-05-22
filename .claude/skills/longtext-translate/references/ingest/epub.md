# EPUB → Markdown 规范化

本文档说明如何将 EPUB 文件中指定章节转换为可供翻译流程使用的干净 Markdown。目标不是完整复刻 EPUB 包装结构，而是得到干净正文：保留章节标题、段落、强调和图片，去掉目录、导航、脚注、封面版权等不属于目标正文的干扰信息。

## 确认边界

开始处理前先把源材料具体化：EPUB 路径、用户要抽取的章节或 spine 范围、输出目录。

若用户给的是“前三章”“第 4～107 页”这类表达，不要想当然把页码等同于 EPUB 内部顺序；先读取 EPUB spine，确认哪些 XHTML 文件对应目标内容。

若发现用户给的页码或范围会包含下一章封面、版权页、目录或其他非目标内容，先指出边界问题并让用户确认是“严格按范围”还是“按内容到章节结束”。

## 推荐输出结构

将输出放在一个独立目录中，避免和源文件混在一起：

```text
输出目录/
├── book_first_three_chapters.md
└── images/
    ├── 1.01_sou-book.jpg
    └── ...
```

Markdown 中图片使用本地相对路径：`![](images/example.jpg)`

## 使用提取脚本

优先使用 `{baseDir}/scripts/ingest/epub.py`。`{baseDir}` 为此 `SKILL.md` 所在目录路径。

### 列出 spine

```bash
python3 {baseDir}/scripts/ingest/epub.py path/to/book.epub --list-spine
```

输出左侧的序号就是后续 `--spine-start` 和 `--spine-end` 使用的 spine 序号，从 0 开始计数。

### 按 href 指定章节

```bash
python3 {baseDir}/scripts/ingest/epub.py \
  path/to/book.epub \
  --href Text/Introduction.xhtml \
  --href Text/Chapter1.xhtml \
  --href Text/Chapter1-text.xhtml \
  --output path/to/output/book_first_chapters.md
```

### 按 spine 序号范围

```bash
python3 {baseDir}/scripts/ingest/epub.py \
  path/to/book.epub \
  --spine-start 4 \
  --spine-end 14 \
  --output path/to/output/selection.md
```

`--spine-start` 和 `--spine-end` 都是闭区间，且以 `--list-spine` 输出的 0-based 序号为准。执行前仍应人工确认边界是否正好落在目标章节。

## 清理原则

干净 Markdown 的判断标准：读者打开文件时只看到正文和必要图片，不需要理解 EPUB 内部结构。

默认删除：
- 目录页、导航页、landmarks
- EPUB 内部锚点和 wrapper（`<span id="...">`、`<div class="image">` 等）
- 脚注区块和脚注回链（除非用户明确要求保留脚注）
- 排版用途的空白块、水平线、CSS class、无意义 id

默认保留：
- 正文章节标题和小标题
- 正文段落、列表、引用
- 粗体、斜体等影响语义或阅读的强调
- 正文内图片，使用本地相对路径

## 验证清单

抽取完成后检查：

- Markdown 文件路径和大小是否合理
- 图片目录路径和图片数量
- 图片引用是否全部存在
- 是否有 `�` 等乱码替换字符
- 是否有残留 HTML 标签
- 是否按用户确认的章节边界截断

若校验发现边界可疑，不要自行修正成看似合理的范围；先说明观察到的内容，例如“最后一页已经进入 Chapter 4 封面”，再请用户确认。
