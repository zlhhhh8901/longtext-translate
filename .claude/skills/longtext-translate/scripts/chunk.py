#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from markdown_it import MarkdownIt


PLAN_VERSION = 1
SPLITTER_VERSION = "markdown-block-v1"


@dataclass
class Block:
    kind: str
    md: str
    words: int


@dataclass(frozen=True)
class Segment:
    id: str
    kind: str
    md: str
    words: int


@dataclass
class SourceModel:
    source: Path
    source_sha256: str
    frontmatter: str
    segments: list[Segment]
    chunks: list[list[str]]
    max_words: int


parser = MarkdownIt("js-default", {"html": True})


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    commands = {"preview", "materialize"}
    if argv and argv[0] not in commands and argv[0] not in {"-h", "--help"}:
        argv = ["materialize", *argv]

    ap = argparse.ArgumentParser(
        prog=Path(sys.argv[0]).name,
        usage="%(prog)s {preview,materialize} <file> [options]",
    )
    subparsers = ap.add_subparsers(dest="command", required=True)

    preview = subparsers.add_parser("preview", help="Generate a self-contained chunk preview HTML")
    add_common_args(preview)

    materialize = subparsers.add_parser("materialize", help="Write final chunk files")
    add_common_args(materialize)
    materialize.add_argument("--plan-json", default=None, help="Adjusted compact plan JSON copied from the preview HTML")
    materialize.add_argument("--plan-file", default=None, metavar="FILE", help="Adjusted compact plan JSON file")

    args = ap.parse_args(argv)

    try:
        if args.command == "preview":
            result = create_preview(args.file, args.max_words, args.output_dir)
        else:
            if args.plan_json and args.plan_file:
                ap.error("--plan-json and --plan-file are mutually exclusive")
            result = materialize_chunks(
                args.file,
                args.max_words,
                args.output_dir,
                plan_json=args.plan_json,
                plan_file=args.plan_file,
            )
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False))
    return 0


def add_common_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("file")
    ap.add_argument("--max-words", type=parse_positive_int, default=5000)
    ap.add_argument("--output-dir", default="")


def parse_positive_int(value: str) -> int:
    try:
        parsed = int(value, 10)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid --max-words value: {value}") from None
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"Invalid --max-words value: {value}")
    return parsed


def create_preview(file: str, max_words: int = 5000, output_dir: str = "") -> dict[str, object]:
    model = build_source_model(file, max_words)
    output_root = resolve_output_root(model.source, output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    preview_path = output_root / "chunk-preview.html"
    data = {
        "version": PLAN_VERSION,
        "source_name": model.source.name,
        "source_sha256": model.source_sha256,
        "splitter": SPLITTER_VERSION,
        "max_words": model.max_words,
        "segments": [
            {"id": segment.id, "kind": segment.kind, "words": segment.words, "text": segment.md}
            for segment in model.segments
        ],
        "chunks": model.chunks,
    }

    template_path = Path(__file__).with_name("chunk-preview.html")
    template = template_path.read_text(encoding="utf-8")
    if "__CHUNK_PREVIEW_DATA__" not in template:
        raise ValueError(f"Preview template missing data placeholder: {template_path}")

    preview_path.write_text(
        template.replace("__CHUNK_PREVIEW_DATA__", json_for_script(data)),
        encoding="utf-8",
    )

    return {
        "source": file,
        "preview_file": str(preview_path),
        "chunks": len(model.chunks),
        "words_per_chunk": chunk_word_counts(model.segments, model.chunks),
    }


def materialize_chunks(
    file: str,
    max_words: int = 5000,
    output_dir: str = "",
    plan_json: str | None = None,
    plan_file: str | None = None,
) -> dict[str, object]:
    plan = read_adjusted_plan(plan_json=plan_json, plan_file=plan_file)
    effective_max_words = int(plan.get("max_words", max_words)) if plan else max_words
    model = build_source_model(file, effective_max_words)
    output_root = resolve_output_root(model.source, output_dir)
    chunks = validate_plan(plan, model) if plan else model.chunks
    chunk_dir = write_chunk_files(model, chunks, output_root)

    return {
        "source": file,
        "chunks": len(chunks),
        "output_dir": str(chunk_dir),
        "frontmatter": bool(model.frontmatter),
        "words_per_chunk": chunk_word_counts(model.segments, chunks),
    }


def resolve_output_root(source: Path, output_dir: str) -> Path:
    return Path(output_dir) if output_dir else source.parent


def build_source_model(file: str, max_words: int) -> SourceModel:
    source = Path(file)
    raw_content = normalize_newlines(source.read_text(encoding="utf-8"))
    frontmatter, body = extract_frontmatter(raw_content)
    blocks = parse_markdown(body)
    segments = build_segments(blocks, max_words)
    return SourceModel(
        source=source,
        source_sha256=sha256_text(raw_content),
        frontmatter=frontmatter,
        segments=segments,
        chunks=build_default_chunks(segments, max_words),
        max_words=max_words,
    )


def read_adjusted_plan(plan_json: str | None, plan_file: str | None) -> dict[str, Any] | None:
    if plan_file:
        text = Path(plan_file).read_text(encoding="utf-8")
    elif plan_json:
        text = plan_json
    else:
        return None

    parsed = json.loads(strip_code_fence(text))
    if not isinstance(parsed, dict):
        raise ValueError("Adjusted plan must be a JSON object")
    return parsed


def strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def validate_plan(plan: dict[str, Any], model: SourceModel) -> list[list[str]]:
    if plan.get("version") != PLAN_VERSION:
        raise ValueError(f"Unsupported plan version: {plan.get('version')}")
    if plan.get("source_sha256") != model.source_sha256:
        raise ValueError("Adjusted plan does not match the current source file")
    if plan.get("splitter") != SPLITTER_VERSION:
        raise ValueError(f"Unsupported splitter: {plan.get('splitter')}")
    if plan.get("max_words") != model.max_words:
        raise ValueError("Adjusted plan max_words does not match the current splitter settings")

    raw_chunks = plan.get("chunks")
    if not isinstance(raw_chunks, list):
        raise ValueError("Adjusted plan must contain a chunks array")

    chunks: list[list[str]] = []
    for index, raw_chunk in enumerate(raw_chunks, 1):
        if not isinstance(raw_chunk, list):
            raise ValueError(f"Chunk {index} must be an array of segment IDs")
        if not raw_chunk:
            raise ValueError(f"Chunk {index} is empty")
        chunk: list[str] = []
        for segment_id in raw_chunk:
            if not isinstance(segment_id, str):
                raise ValueError(f"Chunk {index} contains a non-string segment ID")
            chunk.append(segment_id)
        chunks.append(chunk)

    expected_ids = [segment.id for segment in model.segments]
    actual_ids = [segment_id for chunk in chunks for segment_id in chunk]
    if not expected_ids and not chunks:
        return chunks
    if actual_ids != expected_ids:
        raise ValueError("Adjusted plan must include every segment exactly once in the original order")

    return chunks


def write_chunk_files(model: SourceModel, chunks: list[list[str]], output_root: Path) -> Path:
    chunk_dir = output_root / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    for old_chunk in chunk_dir.glob("chunk-*.md"):
        if re.fullmatch(r"chunk-\d+\.md", old_chunk.name):
            old_chunk.unlink()

    frontmatter_path = chunk_dir / "frontmatter.md"
    if model.frontmatter:
        frontmatter_path.write_text(model.frontmatter, encoding="utf-8")
    elif frontmatter_path.exists():
        frontmatter_path.unlink()

    segment_map = {segment.id: segment for segment in model.segments}
    for index, chunk in enumerate(chunks, 1):
        text = "\n\n".join(segment_map[segment_id].md for segment_id in chunk)
        (chunk_dir / f"chunk-{index:02d}.md").write_text(text, encoding="utf-8")

    return chunk_dir


def normalize_newlines(text: str) -> str:
    return text.removeprefix("﻿").replace("\r\n", "\n").replace("\r", "\n")


def trim_boundary_blank_lines(text: str) -> str:
    return re.sub(r"\n+$", "", re.sub(r"^\n+", "", text))


def extract_frontmatter(content: str) -> tuple[str, str]:
    lines = content.split("\n")
    if not lines or lines[0] != "---":
        return "", content

    for index in range(1, len(lines)):
        if lines[index] in {"---", "..."}:
            return "\n".join(lines[: index + 1]), "\n".join(lines[index + 1 :]).lstrip("\n")

    return "", content


def parse_markdown(content: str) -> list[Block]:
    if not content.strip():
        return []

    lines = content.split("\n")
    blocks: list[Block] = []

    for token in parser.parse(content, {}):
        if not token.map or token.level != 0:
            continue
        if token.nesting not in {0, 1}:
            continue

        start_line, end_line = token.map
        md = trim_boundary_blank_lines("\n".join(lines[start_line:end_line]))
        if not md:
            continue

        blocks.append(make_block(token_type_to_block_kind(token.type), md))

    if not blocks:
        body = trim_boundary_blank_lines(content)
        if body:
            blocks.append(make_block("flow", body))

    return blocks


def token_type_to_block_kind(token_type: str) -> str:
    if token_type == "heading_open":
        return "heading"
    if token_type == "hr":
        return "thematicBreak"
    if token_type == "html_block":
        return "html"
    if token_type in {"fence", "code_block"}:
        return "code"
    return "flow"


def make_block(kind: str, md: str) -> Block:
    trimmed = trim_boundary_blank_lines(md)
    return Block(kind=kind, md=trimmed, words=count_words(trimmed))


def build_segments(blocks: list[Block], max_words_per_chunk: int) -> list[Segment]:
    segments: list[Segment] = []
    for block in blocks:
        for split_block in split_oversized_block(block, max_words_per_chunk):
            segments.append(
                Segment(
                    id=f"seg-{len(segments) + 1:06d}",
                    kind=split_block.kind,
                    md=split_block.md,
                    words=split_block.words,
                )
            )
    return segments


def build_default_chunks(segments: list[Segment], max_words_per_chunk: int) -> list[list[str]]:
    chunks: list[list[str]] = []
    current_ids: list[str] = []
    current_words = 0

    def flush_current() -> None:
        nonlocal current_ids, current_words
        if current_ids:
            chunks.append(current_ids)
            current_ids = []
            current_words = 0

    for section in split_segments_into_sections(segments):
        section_words = sum(segment.words for segment in section)
        if section_words <= max_words_per_chunk:
            if current_ids and current_words + section_words > max_words_per_chunk:
                flush_current()
            current_ids.extend(segment.id for segment in section)
            current_words += section_words
            continue

        flush_current()
        for segment in section:
            if current_ids and current_words + segment.words > max_words_per_chunk:
                flush_current()
            current_ids.append(segment.id)
            current_words += segment.words

    flush_current()
    return chunks


def split_segments_into_sections(segments: list[Segment]) -> list[list[Segment]]:
    sections: list[list[Segment]] = []
    current: list[Segment] = []

    for segment in segments:
        if segment.kind == "heading" and current:
            sections.append(current)
            current = [segment]
            continue
        current.append(segment)

    if current:
        sections.append(current)

    return sections


def split_oversized_block(block: Block, max_words_per_chunk: int) -> list[Block]:
    if block.words <= max_words_per_chunk:
        return [block]

    if block.kind in {"heading", "thematicBreak", "html", "code"}:
        return [block]

    lines = block.md.split("\n")
    if len(lines) <= 1:
        return [block]

    split_blocks: list[Block] = []
    buffer: list[str] = []
    buffer_words = 0

    for line in lines:
        line_words = count_words(line)
        if buffer_words + line_words > max_words_per_chunk and buffer:
            split_blocks.append(make_block(block.kind, "\n".join(buffer)))
            buffer = [line]
            buffer_words = line_words
            continue

        buffer.append(line)
        buffer_words += line_words

    if buffer:
        split_blocks.append(make_block(block.kind, "\n".join(buffer)))

    return split_blocks


def chunk_word_counts(segments: list[Segment], chunks: list[list[str]]) -> list[int]:
    word_map = {segment.id: segment.words for segment in segments}
    return [sum(word_map[segment_id] for segment_id in chunk) for chunk in chunks]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def json_for_script(data: dict[str, Any]) -> str:
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return encoded.replace("</", "<\\/").replace(" ", "\\u2028").replace(" ", "\\u2029")


def count_words(text: str) -> int:
    cleaned = re.sub(r"[#*`\[\]()>|_~-]", " ", text)
    cjk = re.findall(r"[一-鿿㐀-䶿豈-﫿]", cleaned)
    latin = re.findall(r"[a-zA-Z0-9]+", cleaned)
    return len(cjk) + len(latin)


if __name__ == "__main__":
    raise SystemExit(main())
