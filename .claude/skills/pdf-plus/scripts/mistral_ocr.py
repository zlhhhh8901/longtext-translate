#!/usr/bin/env python3
"""
Mistral OCR - High-quality PDF/Image text extraction using Mistral AI's OCR API.

This script provides comprehensive OCR capabilities using Mistral's document AI,
supporting PDF documents and images with advanced features like table extraction,
header/footer detection, and structured output.

Requirements:
    pip install mistralai

Environment:
    MISTRAL_API_KEY: Your Mistral API key (required)

Usage:
    # Basic usage - extract text from PDF
    python mistral_ocr.py document.pdf

    # Extract with table formatting as markdown
    python mistral_ocr.py document.pdf --table-format markdown

    # Extract with table formatting as HTML
    python mistral_ocr.py document.pdf --table-format html

    # Include base64 encoded images in output
    python mistral_ocr.py document.pdf --include-images

    # Extract headers and footers (OCR 2512+)
    python mistral_ocr.py document.pdf --extract-headers --extract-footers

    # Save output to file
    python mistral_ocr.py document.pdf -o output.md

    # Process from URL
    python mistral_ocr.py --url https://example.com/document.pdf

    # Process an image
    python mistral_ocr.py image.png

    # Output as JSON (full API response)
    python mistral_ocr.py document.pdf --json
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Optional


def get_client():
    """Initialize Mistral client with API key from environment."""
    try:
        from mistralai import Mistral
    except ImportError:
        print("Error: mistralai package not installed.", file=sys.stderr)
        print("Install with: pip install mistralai", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("Error: MISTRAL_API_KEY environment variable not set.", file=sys.stderr)
        print("Set it with: export MISTRAL_API_KEY='your-api-key'", file=sys.stderr)
        sys.exit(1)

    return Mistral(api_key=api_key)


def file_to_base64(file_path: str) -> str:
    """Convert a file to base64 encoded string."""
    with open(file_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def get_mime_type(file_path: str) -> str:
    """Determine MIME type based on file extension."""
    ext = Path(file_path).suffix.lower()
    mime_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".avif": "image/avif",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    return mime_types.get(ext, "application/octet-stream")


def is_image_file(file_path: str) -> bool:
    """Check if file is an image based on extension."""
    ext = Path(file_path).suffix.lower()
    return ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif"}


def process_document(
    client,
    file_path: Optional[str] = None,
    url: Optional[str] = None,
    table_format: Optional[str] = None,
    include_image_base64: bool = False,
    extract_header: bool = False,
    extract_footer: bool = False,
) -> dict:
    """
    Process a document using Mistral OCR.

    Args:
        client: Mistral client instance
        file_path: Path to local file (PDF or image)
        url: URL to document
        table_format: Format for tables - None, "markdown", or "html"
        include_image_base64: Include base64 encoded images in response
        extract_header: Extract headers (OCR 2512+)
        extract_footer: Extract footers (OCR 2512+)

    Returns:
        OCR response as dictionary
    """
    # Build document parameter
    if url:
        if is_image_file(url):
            document = {
                "type": "image_url",
                "image_url": url
            }
        else:
            document = {
                "type": "document_url",
                "document_url": url
            }
    elif file_path:
        base64_data = file_to_base64(file_path)
        mime_type = get_mime_type(file_path)

        if is_image_file(file_path):
            document = {
                "type": "image_url",
                "image_url": f"data:{mime_type};base64,{base64_data}"
            }
        else:
            document = {
                "type": "document_url",
                "document_url": f"data:{mime_type};base64,{base64_data}"
            }
    else:
        raise ValueError("Either file_path or url must be provided")

    # Build OCR request parameters
    ocr_params = {
        "model": "mistral-ocr-latest",
        "document": document,
        "include_image_base64": include_image_base64,
    }

    if table_format:
        ocr_params["table_format"] = table_format

    if extract_header:
        ocr_params["extract_header"] = True

    if extract_footer:
        ocr_params["extract_footer"] = True

    # Process document
    response = client.ocr.process(**ocr_params)

    return response


def extract_markdown(response) -> str:
    """Extract markdown content from OCR response."""
    markdown_parts = []

    for i, page in enumerate(response.pages):
        if len(response.pages) > 1:
            markdown_parts.append(f"\n<!-- Page {i + 1} -->\n")
        markdown_parts.append(page.markdown)

    return "\n".join(markdown_parts)


def format_response_json(response) -> str:
    """Format OCR response as JSON string."""
    # Convert response to dictionary for JSON serialization
    result = {
        "pages": []
    }

    for page in response.pages:
        page_data = {
            "markdown": page.markdown,
            "index": page.index if hasattr(page, 'index') else None,
        }

        # Add optional fields if present
        if hasattr(page, 'images') and page.images:
            page_data["images"] = [
                {
                    "id": img.id if hasattr(img, 'id') else None,
                    "base64": img.image_base64 if hasattr(img, 'image_base64') else None,
                }
                for img in page.images
            ]

        if hasattr(page, 'dimensions') and page.dimensions:
            page_data["dimensions"] = {
                "width": page.dimensions.width if hasattr(page.dimensions, 'width') else None,
                "height": page.dimensions.height if hasattr(page.dimensions, 'height') else None,
                "dpi": page.dimensions.dpi if hasattr(page.dimensions, 'dpi') else None,
            }

        result["pages"].append(page_data)

    return json.dumps(result, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF/images using Mistral OCR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to PDF or image file"
    )
    parser.add_argument(
        "--url",
        help="URL to document (alternative to local file)"
    )
    parser.add_argument(
        "--table-format",
        choices=["markdown", "html"],
        help="Format for extracted tables"
    )
    parser.add_argument(
        "--include-images",
        action="store_true",
        help="Include base64 encoded images in output"
    )
    parser.add_argument(
        "--extract-headers",
        action="store_true",
        help="Extract headers (requires OCR 2512+)"
    )
    parser.add_argument(
        "--extract-footers",
        action="store_true",
        help="Extract footers (requires OCR 2512+)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full JSON response instead of markdown"
    )

    args = parser.parse_args()

    # Validate input
    if not args.file and not args.url:
        parser.error("Either FILE or --url must be provided")

    if args.file and not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Initialize client
    client = get_client()

    # Process document
    try:
        response = process_document(
            client=client,
            file_path=args.file,
            url=args.url,
            table_format=args.table_format,
            include_image_base64=args.include_images,
            extract_header=args.extract_headers,
            extract_footer=args.extract_footers,
        )
    except Exception as e:
        print(f"Error processing document: {e}", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.json:
        output = format_response_json(response)
    else:
        output = extract_markdown(response)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
