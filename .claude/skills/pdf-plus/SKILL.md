---
name: pdf
description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or programmatically process, generate, or analyze PDF documents at scale.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see reference.md. If you need to fill out a PDF form, read forms.md and follow its instructions.

**For high-quality OCR** (scanned documents, complex layouts, or when standard extraction fails), use Mistral OCR - see mistral_ocr.md for detailed instructions.

## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Add a line
c.line(100, height - 140, 400, height - 140)

# Save
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Page 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Build PDF
doc.build(story)
```

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Mistral OCR (Recommended for Complex Documents)

For scanned documents, complex layouts, or when standard extraction produces poor results, use Mistral OCR for superior accuracy.

```python
# Requires: pip install mistralai
# Set MISTRAL_API_KEY environment variable
import os
from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# From URL
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": "https://example.com/document.pdf"
    },
    table_format="markdown"  # Preserve table structure
)

# Extract text from all pages
for page in ocr_response.pages:
    print(page.markdown)
```

Or use the included script:
```bash
# Basic extraction
python scripts/mistral_ocr.py document.pdf -o output.md

# With table formatting
python scripts/mistral_ocr.py document.pdf --table-format markdown -o output.md
```

#### When to Use Mistral OCR Parameters

**IMPORTANT: Only when the user explicitly wants to use Mistral OCR**, ask about their parameter preferences using these guidelines:

**table_format** (default: None)
- Ask: "Do you need table formatting?"
- Use `markdown` for most cases (preserves structure, readable)
- Use `html` if user needs HTML output
- Use `None` if document has no tables or user doesn't need table structure

**include_image_base64** (default: False)
- Ask: "Do you need to extract embedded images?"
- Use `True` only if user needs to extract/save images from the document
- Use `False` for text-only extraction (saves bandwidth and cost)

**extract_header/extract_footer** (default: False)
- Ask: "Do you need headers and footers extracted?"
- Use `True` for formal documents (reports, papers, legal documents)
- Use `False` for casual documents or when headers/footers are not needed
- Note: Requires OCR 2512 or newer

**Example interaction when user wants Mistral OCR:**
```
User: "Use Mistral OCR to extract text from this PDF"
Claude: "I'll use Mistral OCR. A few questions about the extraction:
- Does the document contain tables that need formatting? (markdown/html/none)
- Do you need to extract embedded images?
- Should I extract headers and footers?"
```

See mistral_ocr.md for complete documentation including local file processing, batch operations, and advanced options.

#### Post-process OCR Markdown for Page-Break Paragraph Splits

After removing page markers, page numbers, headers, and footers, always check whether the original page break left a false blank line inside a sentence or paragraph. This is common when OCR output is page-based: the previous page ends mid-sentence, the next page begins with the continuation, and cleanup removes the page furniture but leaves an empty line between the two fragments.

Use a conservative repair pass, not global blank-line compression:

1. Keep the raw OCR output for comparison.
2. Remove obvious page furniture first: page comments, repeated headers/footers, and standalone page numbers.
3. Scan every blank line with the previous and next non-empty lines. Treat it as a likely page-break split only when the surrounding text gives strong evidence of continuity:
   - The previous line ends without sentence-ending punctuation, such as `.`, `?`, `!`, `。`, `？`, `！`, `;`, `；`, closing quotes/brackets, or a code fence.
   - The next line starts like a continuation: lowercase English, a word fragment, or the second half of a Chinese word or phrase.
   - The surrounding text matches a page boundary in the raw OCR output.
4. Join only those lines. Use no separator for CJK word fragments, and a single space for English prose unless the break is clearly inside a hyphenated word.
5. Do not join across headings, block quotes, code fences, lists, tables, bibliographies, footnotes, figure captions, or true paragraph starts.
6. Re-read representative areas around every join, especially document openings, footnotes, and references.

This method is mature enough as a **review-guided post-processing heuristic**, not as a fully automatic proof of correctness. It is safe when joins are restricted to obvious page-boundary continuations and verified against context. The main risk is false positives: a real paragraph break can also occur after a line that lacks punctuation, and notes or headings can look like continuations. Avoid broad rules such as "delete all blank lines after non-punctuation"; they will damage paragraph structure. When uncertain, leave the blank line in place and report the ambiguity.

For long documents, write a short script that prints candidate blank lines with previous/next snippets, review the candidate list, then apply an explicit allowlist of joins. A useful verification script should report remaining suspicious blank lines rather than silently changing them.

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

# Create watermark (or load existing)
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs (basic) | pytesseract | Convert to image first |
| OCR scanned PDFs (high quality) | Mistral OCR | `scripts/mistral_ocr.py` |
| Complex document OCR | Mistral OCR | See mistral_ocr.md |
| Fill PDF forms | pdf-lib or pypdf (see forms.md) | See forms.md |

## Next Steps

- For advanced pypdfium2 usage, see reference.md
- For JavaScript libraries (pdf-lib), see reference.md
- If you need to fill out a PDF form, follow the instructions in forms.md
- For high-quality OCR with Mistral, see mistral_ocr.md
- For troubleshooting guides, see reference.md
