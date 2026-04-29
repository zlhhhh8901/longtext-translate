# Mistral OCR Reference

This document provides detailed information about using Mistral AI's OCR capabilities for high-quality text extraction from PDF documents and images.

## Overview

Mistral OCR (`mistral-ocr-latest`) is a powerful document AI model that extracts text and structured content from PDF documents and images. It provides superior accuracy compared to traditional OCR methods, especially for:

- Complex layouts with multiple columns
- Tables and structured data
- Mixed content (text, images, diagrams)
- Scanned documents
- Handwritten text

## Requirements

### Installation

```bash
pip install mistralai
```

### Authentication

Set the `MISTRAL_API_KEY` environment variable:

```bash
export MISTRAL_API_KEY="your-api-key"
```

Get your API key from the [Mistral AI Console](https://console.mistral.ai/).

## Using the Script

The `scripts/mistral_ocr.py` script provides a command-line interface for Mistral OCR.

### Basic Usage

```bash
# Extract text from PDF
python scripts/mistral_ocr.py document.pdf

# Extract text from image
python scripts/mistral_ocr.py scan.png

# Save output to file
python scripts/mistral_ocr.py document.pdf -o output.md
```

### Table Extraction

```bash
# Extract tables as markdown
python scripts/mistral_ocr.py document.pdf --table-format markdown

# Extract tables as HTML
python scripts/mistral_ocr.py document.pdf --table-format html
```

### Advanced Options

```bash
# Include base64 encoded images in output
python scripts/mistral_ocr.py document.pdf --include-images

# Extract headers and footers (OCR 2512+)
python scripts/mistral_ocr.py document.pdf --extract-headers --extract-footers

# Output full JSON response
python scripts/mistral_ocr.py document.pdf --json

# Process from URL
python scripts/mistral_ocr.py --url https://arxiv.org/pdf/2201.04234
```

## Python API Usage

### Basic Text Extraction

```python
import os
from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# From URL
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": "https://arxiv.org/pdf/2201.04234"
    }
)

# Extract markdown from all pages
for page in ocr_response.pages:
    print(page.markdown)
```

### From Local File

```python
import base64
import os
from mistralai import Mistral

def file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# Read and encode local PDF
pdf_base64 = file_to_base64("document.pdf")

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": f"data:application/pdf;base64,{pdf_base64}"
    }
)

# Process results
for i, page in enumerate(ocr_response.pages):
    print(f"=== Page {i + 1} ===")
    print(page.markdown)
```

### Table Extraction with Formatting

```python
# Extract tables as markdown
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": "https://example.com/report.pdf"
    },
    table_format="markdown"  # or "html"
)

# Tables will be formatted in the markdown output
for page in ocr_response.pages:
    print(page.markdown)
```

### Image OCR

```python
import base64
from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# From URL
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "image_url",
        "image_url": "https://example.com/scan.png"
    }
)

# From local file
with open("scan.png", "rb") as f:
    image_base64 = base64.standard_b64encode(f.read()).decode("utf-8")

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "image_url",
        "image_url": f"data:image/png;base64,{image_base64}"
    }
)
```

### Extract Embedded Images

```python
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": "https://example.com/document.pdf"
    },
    include_image_base64=True
)

# Access extracted images
for page in ocr_response.pages:
    if hasattr(page, 'images') and page.images:
        for img in page.images:
            # img.image_base64 contains the base64 encoded image
            # img.id contains the image identifier
            print(f"Found image: {img.id}")
```

### Header and Footer Extraction

```python
# Available for OCR 2512 or newer
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": "https://example.com/document.pdf"
    },
    extract_header=True,
    extract_footer=True
)
```

## Response Structure

The OCR response contains:

```python
ocr_response.pages  # List of pages

# Each page contains:
page.markdown       # Raw markdown content
page.index         # Page index (0-based)
page.images        # List of extracted images (if include_image_base64=True)
page.tables        # List of extracted tables
page.hyperlinks    # List of detected hyperlinks
page.dimensions    # Page dimensions (width, height, dpi)
```

## Supported File Types

### Documents
- PDF (`.pdf`)
- PowerPoint (`.pptx`)
- Word (`.docx`)

### Images
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- GIF (`.gif`)
- WebP (`.webp`)
- AVIF (`.avif`)

## Comparison with Other Methods

| Method | Best For | Accuracy | Speed |
|--------|----------|----------|-------|
| Mistral OCR | Complex documents, scans | Excellent | Moderate |
| pdfplumber | Native PDFs with tables | Good | Fast |
| pypdf | Simple native PDFs | Moderate | Very Fast |
| pytesseract | Simple scanned images | Moderate | Slow |

### When to Use Mistral OCR

- Scanned documents requiring high accuracy
- Complex layouts with mixed content
- Documents with tables requiring structure preservation
- When other methods produce poor results
- Handwritten or difficult-to-read text

### When to Use Traditional Methods

- Simple native PDFs (use pypdf or pdfplumber)
- Budget constraints (Mistral OCR has API costs)
- Offline processing requirements
- Very high volume processing

## Error Handling

```python
from mistralai import Mistral
from mistralai.exceptions import MistralAPIException

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

try:
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": "https://example.com/document.pdf"
        }
    )
except MistralAPIException as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## Batch Processing

```python
import os
from pathlib import Path
from mistralai import Mistral

def batch_ocr(input_dir: str, output_dir: str):
    """Process all PDFs in a directory."""
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for pdf_file in input_path.glob("*.pdf"):
        print(f"Processing: {pdf_file.name}")

        try:
            # Read and encode file
            with open(pdf_file, "rb") as f:
                pdf_base64 = base64.standard_b64encode(f.read()).decode("utf-8")

            # Process with OCR
            response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{pdf_base64}"
                },
                table_format="markdown"
            )

            # Extract and save markdown
            markdown = "\n\n".join(page.markdown for page in response.pages)
            output_file = output_path / f"{pdf_file.stem}.md"
            output_file.write_text(markdown, encoding="utf-8")

            print(f"  -> Saved: {output_file.name}")

        except Exception as e:
            print(f"  -> Error: {e}")

# Usage
batch_ocr("./pdfs", "./output")
```

## Cost Considerations

Mistral OCR is a paid API service. Consider:

- Number of pages processed
- Frequency of processing
- Whether to use `include_image_base64` (increases response size)
- Caching results for repeated access

For high-volume or budget-sensitive applications, consider using traditional methods for simple documents and reserving Mistral OCR for complex cases.
