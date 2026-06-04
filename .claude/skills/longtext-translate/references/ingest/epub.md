# EPUB → Markdown 规范化

本文档说明如何将 EPUB 中的指定内容转换为可供翻译流程使用的干净 Markdown。输出应保留章节标题、正文段落、语义性强调、列表、引用和必要图片，并排除目录、导航、封面、版权页、脚注回链等干扰内容。

## 总体流程

1. 确认 EPUB 路径和用户要翻译的内容范围。
2. 读取 EPUB spine，定位目标章节或 XHTML 文件。
3. 确认抽取边界。
4. 运行提取脚本，生成 Markdown 和本地图片目录。
5. 检查 Markdown、图片引用、乱码字符和残留 HTML。
6. 使用规范化后的 Markdown 进入翻译方案确认。

## 边界确认

用户给出“前三章”“第 4～107 页”等表达时，不要直接把它们等同于 EPUB 内部顺序。先读取 spine，确认哪些 XHTML 文件对应目标内容。

若目标范围包含下一章封面、版权页、目录或其他非正文内容，先说明观察到的边界情况，并让用户确认是严格按范围抽取，还是按正文内容边界抽取。

## 输出命名

规范化 Markdown 默认保存到源 EPUB 同级目录，文件名从 EPUB basename 派生。文件名只做轻度路径清理：替换路径不安全字符、压缩连续空白、去掉首尾空白，必要时截断过长文件名。

整本或单一主体内容：

```text
books/example.epub
books/example.md
books/example_images/
```

部分章节：

```text
books/example.epub
books/example-chapters-1-3.md
books/example-chapters-1-3_images/
```

Markdown 中图片使用本地相对路径，例如 `![](example_images/cover.jpg)`。每个规范化 Markdown 使用独立图片目录，避免不同抽取结果互相覆盖。

## 使用提取脚本

优先使用 `{baseDir}/scripts/ingest/epub.py`。`{baseDir}` 为此 `SKILL.md` 所在目录路径。

### 列出 spine

```bash
python3 {baseDir}/scripts/ingest/epub.py path/to/book.epub --list-spine
```

输出左侧序号就是后续 `--spine-start` 和 `--spine-end` 使用的 0-based spine 序号。

### 按 href 指定章节

```bash
python3 {baseDir}/scripts/ingest/epub.py \
  path/to/book.epub \
  --href Text/Introduction.xhtml \
  --href Text/Chapter1.xhtml \
  --href Text/Chapter1-text.xhtml \
  --output path/to/book-chapters-1-3.md \
  --image-dir-name book-chapters-1-3_images
```

### 按 spine 序号范围

```bash
python3 {baseDir}/scripts/ingest/epub.py \
  path/to/book.epub \
  --spine-start 4 \
  --spine-end 14 \
  --output path/to/book-chapters-1-3.md \
  --image-dir-name book-chapters-1-3_images
```

`--spine-start` 和 `--spine-end` 都是闭区间。执行前根据 `--list-spine` 的结果确认边界。

## 清理原则

干净 Markdown 的判断标准：读者打开文件时只看到目标正文和必要图片，不需要理解 EPUB 内部结构。

默认排除：

- 目录页、导航页、landmarks；
- 封面、版权页、广告页等非目标正文；
- EPUB 内部锚点和 wrapper，例如 `<span id="...">`、`<div class="image">`；
- 排版用途的空白块、水平线、CSS class、无意义 id。

默认保留：

- 正文章节标题和小标题；
- 正文段落、列表、引用；
- 粗体、斜体等影响语义或阅读的强调；
- 正文内图片，使用本地相对路径。

## 验证清单

抽取完成后检查：

- Markdown 文件路径和大小是否合理
- 图片目录路径和图片数量是否合理
- 图片引用是否全部存在
- 是否有 `�` 等乱码替换字符
- 是否有残留 HTML 标签
- 是否按用户确认的章节边界截断

若校验发现边界可疑，不要自行修正成看似合理的范围；先说明观察到的内容，例如“最后一页已经进入 Chapter 4 封面”，再请用户确认。
