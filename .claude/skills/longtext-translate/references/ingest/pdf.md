# PDF → Markdown 规范化

本文档说明如何将 PDF 文件转换为可供翻译流程使用的干净 Markdown。目标不是完整复现 PDF 版面，而是得到准确、完整、结构清晰的正文文本。

## 处理路径

PDF 规范化按以下顺序尝试，选择最先可用的路径：

1. **页码范围预处理**：若用户只要求翻译 PDF 的部分页码，先拆出该页码范围，后续所有提取和 OCR 都只针对拆出的 PDF。
2. **文本层提取**：适用于原生 PDF（文本可选中的常规文档）。
3. **OCR 回退**：适用于扫描件、图片型 PDF，或文本层提取结果明显不完整。

## 页码范围预处理

若用户指定“第 X 页到第 Y 页”“只翻译 10-25 页”等页码范围，先生成只包含该范围的新 PDF，再进入文本层提取或 OCR。不要先抽取整本 PDF 后再从 Markdown 中截取，因为 OCR 和 PDF 文本提取都会受页眉、页脚、断段和页面顺序影响，越早缩小范围越可靠。

页码范围默认解释为 PDF 查看器中的物理页码，从 1 开始计数。若用户说的是书内印刷页码、目录页码、罗马数字页码或章节页码，应先确认它们对应的 PDF 物理页码。

### 使用 qpdf 拆出指定页段

```bash
# 提取 PDF 物理页码第 10-25 页
qpdf input.pdf --pages input.pdf 10-25 -- pages_10_25.pdf
```

后续命令均使用拆出的 `pages_10_25.pdf` 作为输入。例如：

```bash
pdftotext -layout pages_10_25.pdf output.txt
python3 {baseDir}/scripts/ingest/mistral_ocr.py pages_10_25.pdf -o output.md
```

### 没有 qpdf 时使用 pypdf

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for index in range(10 - 1, 25):
    writer.add_page(reader.pages[index])

with open("pages_10_25.pdf", "wb") as f:
    writer.write(f)
```

拆分完成后，保留拆出的 PDF，便于用户核对边界；规范化后的 Markdown 仍保存为翻译流程的唯一输入源。

## 文本层提取

### 快速判断 PDF 类型

```bash
# 查看页数
python3 -c "from pypdf import PdfReader; r = PdfReader('doc.pdf'); print(len(r.pages))"

# 试提取首页文本，判断是否有可用文本层
python3 -c "from pypdf import PdfReader; print(PdfReader('doc.pdf').pages[0].extract_text()[:500] or 'EMPTY')"
```

首页文本为空或明显为乱码时，跳过文本层提取，直接进入 OCR。

### 使用 pdftotext 提取

```bash
# 保留版式的文本提取（多数情况首选）
pdftotext -layout input.pdf output.txt
```

若用户指定页码范围，优先使用“页码范围预处理”拆出新 PDF，再对拆出的 PDF 运行 `pdftotext`。只有在不需要保留页段 PDF 供后续 OCR 或核对时，才直接使用 `pdftotext -f X -l Y input.pdf output.txt`。

### 使用 pypdf 提取

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
text = []
for i, page in enumerate(reader.pages, start=1):
    page_text = page.extract_text() or ""
    text.append(f"\n\n<!-- Page {i} -->\n\n{page_text}")

with open("output.md", "w") as f:
    f.write("".join(text))
```

用 `<!-- Page N -->` 注释保留页序信息，便于后续核对和清理。

### 表格提取

文档包含表格时，使用 pdfplumber：

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page_number, page in enumerate(pdf.pages, start=1):
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                print(" | ".join(str(cell or "") for cell in row))
```

提取结果应以 Markdown 表格格式写入输出文件。

## OCR 回退

文本层提取为空、严重缺失或阅读顺序混乱时，使用 Mistral OCR。

### 安装

```bash
pip install mistralai
```

### API Key 配置

API key 存储在 `~/.config/longtext-translate/.env`（Windows：`%APPDATA%\longtext-translate\.env`）。脚本内部静默加载，正常 setup/OCR 流程不会暴露 key。

**Agent 操作流程**：

1. 使用 OCR 前，先征得用户同意："使用 Mistral OCR 提取 PDF 内容需要将文件上传至 Mistral API 处理。是否继续？"
2. 用户同意后，直接运行 OCR 命令（见下方基本用法）。脚本会自动从配置文件或环境变量 `MISTRAL_API_KEY` 加载 key。
3. 若脚本提示 "MISTRAL_API_KEY not configured"，执行 setup 并引导用户填写：
   ```bash
   python3 {baseDir}/scripts/ingest/mistral_ocr.py --setup
   ```
   将脚本输出的配置文件路径告知用户，引导其用本机编辑器打开并填入 key（如 macOS 可 `open -e <路径>`）。**切勿让用户在聊天中直接发送 key。** 用户确认填写完成后，重新运行 OCR 命令。
4. 若脚本提示 key 验证失败，引导用户检查配置文件中的 key 是否正确。

### 基本用法

```bash
python3 {baseDir}/scripts/ingest/mistral_ocr.py document.pdf -o output.md
```

`{baseDir}` 为此 SKILL.md 所在目录路径。

### 保留表格结构

```bash
python3 {baseDir}/scripts/ingest/mistral_ocr.py document.pdf --table-format markdown -o output.md
```

## 提取后清理

无论使用哪种提取方式，结果都需要清理后再进入翻译流程。

### 必须清理

- 页码标记：单独的页码行、页眉页脚中的页码
- 重复页眉和页脚：每页重复出现的章节名、作者名等
- 页面分隔标记：`<!-- Page N -->` 注释之外的硬分页符

### 段落合并

PDF 提取经常在页边界处产生断裂的段落。合并规则：

1. 只合并明显跨页延续的断行
2. 前一行没有句末标点、后一行明显是延续内容时才合并
3. 标题、列表、表格、脚注、图注、代码块边界保持原样

### 验证清单

清理完成后检查：

- 段落是否完整，无明显的页边界断裂
- 表格是否正确转为 Markdown 表格
- 是否有残留的页码、页眉、页脚
- 是否有 `�` 等乱码替换字符
- 章节标题层级是否正确
- 图片引用是否保留（如图片对理解内容有意义）

若提取质量明显不足以支撑可靠翻译（大面积缺字、段落完全错乱、表格内容不可读），应暂停流程并告知用户当前障碍，而非强行翻译。

## 工具速查

| 场景 | 工具 |
| --- | --- |
| 快速判断文本层 | `pypdf` |
| 保留版式文本 | `pdftotext -layout` |
| 表格提取 | `pdfplumber` |
| 页面渲染核对 | `{baseDir}/scripts/ingest/convert_pdf_to_images.py` |
| 扫描件 / 复杂版式 OCR | `{baseDir}/scripts/ingest/mistral_ocr.py` |
| 页面拆分 | `qpdf` |
