#!/usr/bin/env python3
"""
Mistral OCR - High-quality PDF/Image text extraction using Mistral AI's OCR API.

Use this script when local text extraction is poor, the PDF is scanned, or the
page contains complex tables and layout.

Requirements:
    pip install mistralai

API Key:
    The script loads MISTRAL_API_KEY from environment variable first,
    then falls back to ~/.config/longtext-translate/.env (platform-adaptive).

    First-time setup:
        python mistral_ocr.py --setup

Usage:
    # Extract text from PDF
    python mistral_ocr.py document.pdf

    # Extract with table formatting as markdown
    python mistral_ocr.py document.pdf --table-format markdown

    # Include embedded images in the JSON response
    python mistral_ocr.py document.pdf --include-images --json

    # Extract headers and footers (OCR 2512+)
    python mistral_ocr.py document.pdf --extract-headers --extract-footers

    # Save output to file
    python mistral_ocr.py document.pdf -o output.md

    # Process a page image or scan
    python mistral_ocr.py page.png
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path


# --- Configuration management ---


def get_config_dir() -> Path:
    """Return platform-adaptive config directory."""
    if os.name == "nt":
        base = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(base) / "longtext-translate"
    return Path.home() / ".config" / "longtext-translate"


def load_env_file(env_path: Path) -> dict:
    """Parse a .env file safely without shell execution."""
    if not env_path.exists():
        return {}
    result = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2:
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
            result[key] = value
    return result


def get_api_key() -> str | None:
    """Get API key from environment or .env file. Never prints the key."""
    key = os.environ.get("MISTRAL_API_KEY")
    if key:
        return key
    env_path = get_config_dir() / ".env"
    env_vars = load_env_file(env_path)
    return env_vars.get("MISTRAL_API_KEY")


def setup_config() -> Path:
    """Create config directory and .env template. Returns path to .env file."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    env_path = config_dir / ".env"
    if not env_path.exists():
        env_path.write_text("# LongText-Translate Configuration\nMISTRAL_API_KEY=\n")
    return env_path


def validate_api_key(client) -> None:
    """Validate API key with a lightweight API call. Exits on auth failure."""
    try:
        client.models.list()
    except Exception as e:
        error_msg = str(e)
        if any(kw in error_msg for kw in ["401", "403", "Unauthorized", "Forbidden"]):
            env_path = get_config_dir() / ".env"
            print(
                f"API key validation failed: authentication error.\n"
                f"Please check your key in {env_path}",
                file=sys.stderr,
            )
            sys.exit(1)
        print(
            f"Warning: could not validate API key ({e}). Proceeding anyway.",
            file=sys.stderr,
        )


def get_client():
    """Initialize Mistral client with API key from environment or .env file."""
    try:
        from mistralai import Mistral
    except ImportError:
        print("Error: mistralai package not installed.", file=sys.stderr)
        print("Install with: pip install mistralai", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()
    if not api_key:
        env_path = get_config_dir() / ".env"
        print(
            "MISTRAL_API_KEY not configured.\n"
            "Run with --setup to create a config template,\n"
            f"or set your key in {env_path}",
            file=sys.stderr,
        )
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
    }
    return mime_types.get(ext, "application/octet-stream")


def is_image_file(file_path: str) -> bool:
    """Check if file is an image based on extension."""
    ext = Path(file_path).suffix.lower()
    return ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif"}


def process_document(
    client,
    file_path: str,
    table_format: str | None = None,
    include_image_base64: bool = False,
    extract_header: bool = False,
    extract_footer: bool = False,
) -> dict:
    """Process a local PDF or image using Mistral OCR."""
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
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Create config template and exit"
    )

    args = parser.parse_args()

    if args.setup:
        env_path = setup_config()
        print(f"Configuration template created at: {env_path}")
        print("Please open this file and fill in your MISTRAL_API_KEY.")
        if os.name == "nt":
            print(f"You can use: notepad {env_path}")
        else:
            print(f"You can use: open -e {env_path}")
        return

    if not args.file:
        parser.error("FILE is required")

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Initialize client
    client = get_client()

    # Validate API key before uploading file
    validate_api_key(client)

    # Process document
    try:
        response = process_document(
            client=client,
            file_path=args.file,
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
