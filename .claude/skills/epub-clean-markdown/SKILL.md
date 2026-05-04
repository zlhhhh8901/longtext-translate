---
name: epub-clean-markdown
description: 将 EPUB 的指定章节或 spine 范围转换为干净 Markdown，并把正文图片复制为本地相对路径。用户要求“EPUB 转 Markdown”“只取前几章”“保留图片”“去掉脚注/目录/页眉页脚/杂乱 HTML”“抽取章节文本”时应优先使用本 skill，尤其适合书籍、长文档、章节化电子书的局部抽取，而不是直接把整个 EPUB 粗暴丢给 pandoc。
---

# EPUB 干净 Markdown 抽取

本 skill 用于把 EPUB 中指定章节转换为**可直接阅读和后续处理的 Markdown**。核心目标不是完整复刻 EPUB 包装结构，而是得到干净正文：保留章节标题、段落、强调和图片，去掉目录、导航、脚注、封面版权等不属于目标正文的干扰信息。

## 先确认边界

开始处理前先把源材料具体化：EPUB 路径、用户要抽取的章节或 spine 范围、输出目录、是否保留脚注。若用户给的是“前三章”“第 4～107 页”这类表达，不要想当然把页码等同于 EPUB 内部顺序；先读取 EPUB spine，确认哪些 XHTML 文件对应目标内容。

若发现用户给的页码或范围会包含下一章封面、版权页、目录或其他非目标内容，先指出边界问题并让用户确认是“严格按范围”还是“按内容到章节结束”。

## 推荐输出结构

将输出放在一个独立目录中，避免和源文件混在一起：

```text
输出目录/
├── epub_first_three_chapters.md
└── images/
    ├── 1.01_sou-book.jpg
    └── ...
```

Markdown 中图片一律使用本地相对路径：

```markdown
![](images/example.jpg)
```

## 处理流程

1. **读取 EPUB spine。** EPUB 本质是 zip 包，先解析 `META-INF/container.xml` 找到 OPF，再读取 OPF 的 manifest 和 spine。spine 顺序才是阅读顺序。
2. **选择目标 XHTML。** 根据用户要求选择 spine 中对应文件。章节通常有封面页和正文页，例如 `Chapter1.xhtml` 与 `Chapter1-text.xhtml` 都可能要保留。
3. **解析 XHTML 正文。** 只处理 `<body>` 内内容。跳过 `script`、`style`、`nav`、`aside epub:type="footnote"`、脚注回链、空白分隔块等噪声。
4. **复制图片。** 遇到 `<img src="...">` 时，将相对路径解析回 EPUB 内部文件，复制到输出目录的 `images/` 下，并把 Markdown 引用改成相对路径。
5. **转换为干净 Markdown。** 保留标题层级、段落、列表、引用、粗体、斜体和图片。不要保留 HTML wrapper，例如 `<div class="image">`、`<span id="...">`、CSS class。
6. **验证输出。** 检查 Markdown 中所有本地图片引用都存在；检查没有乱码替换字符 `�`；检查没有明显残留 HTML 标签；检查开头和结尾是否落在用户确认的章节边界。

## 推荐脚本

优先使用 `scripts/extract_epub_clean_md.py`。它封装了本轮任务沉淀出的稳定路径：按 spine 或 href 选择 XHTML，抽取正文，复制图片，去掉脚注和 HTML 包装，并做基础校验。

常用方式：

```bash
python .claude/skills/epub-clean-markdown/scripts/extract_epub_clean_md.py \
  path/to/book.epub \
  --href Text/Introduction.xhtml \
  --href Text/Hey.xhtml \
  --href Text/Chapter1.xhtml \
  --href Text/Chapter1-text.xhtml \
  --output path/to/output/book_first_chapters.md
```

也可以先列出 spine：

```bash
python .claude/skills/epub-clean-markdown/scripts/extract_epub_clean_md.py \
  path/to/book.epub \
  --list-spine
```

如果用户给的是 spine 序号范围，可用：

```bash
python .claude/skills/epub-clean-markdown/scripts/extract_epub_clean_md.py \
  path/to/book.epub \
  --spine-start 4 \
  --spine-end 14 \
  --output path/to/output/selection.md
```

`--spine-end` 是闭区间，便于按用户口头范围执行；执行前仍应人工确认边界是否正好落在目标章节。

## 清理原则

干净 Markdown 的判断标准是：读者打开文件时只看到正文和必要图片，不需要理解 EPUB 内部结构。

默认删除：

- 目录页、导航页、landmarks。
- EPUB 内部锚点和 wrapper，例如 `<span id="...">`、`<div class="image">`。
- 脚注区块和脚注回链，除非用户明确要求保留脚注。
- 只有排版用途的空白块、水平线、CSS class、无意义 id。

默认保留：

- 正文章节标题和小标题。
- 正文段落、列表、引用。
- 粗体、斜体等影响语义或阅读的强调。
- 正文内图片，使用本地相对路径。

## 验证清单

完成后报告这些结果：

- Markdown 文件路径。
- 图片目录路径和图片数量。
- 图片引用是否全部存在。
- 是否发现乱码替换字符。
- 是否仍有残留 HTML 标签。
- 是否按用户确认的章节边界截断。

若校验发现边界可疑，不要自行“修正”成看似合理的范围；先说明观察到的内容，例如“最后一页已经进入 Chapter 4 封面”，再请用户确认。