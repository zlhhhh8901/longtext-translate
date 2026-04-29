# Subagent 翻译提示模板

包含两部分：
1. **`02-prompt.md`**——共享上下文（保存到输出目录）。包含背景、术语表、难点和原则。不包含任务专属指令。
2. **Subagent 启动提示**——启动每个 subagent 时传入的任务指令。每个分块一个 subagent（如果不分块，则每个源文件一个）。

主 agent 读取 `01-analysis.md`（如果存在），将所有相关上下文内联到 `02-prompt.md`，然后用引用该文件的任务指令并行启动 subagent。

将 `{placeholders}` 替换为实际值。quick 模式下省略标注为“如果存在分析”的部分。

---

## 第 1 部分：`02-prompt.md`（共享上下文，保存为文件）

```markdown
You are a professional translator. Your task is to translate markdown content from {source_lang} to {target_lang}.

## Target Audience & Style

**Audience**: {audience description}

**Target style**: {style description — e.g., "storytelling: engaging narrative flow, smooth transitions, vivid phrasing" or custom style from user}

**Source voice** (from analysis, if exists): {Brief description of the original author's voice — formal/conversational, humor, register, sentence rhythm.}

## Content Background

{Inlined from 01-analysis.md if analysis exists: content summary, core argument, author background, context.}

## Glossary

Apply these term translations consistently. First occurrence: include original in parentheses.

{Merged glossary — one per line: English → Translation}

## Translation Challenges

{Inlined from 01-analysis.md §1.4 if analysis exists. Comprehension gaps, figurative language, structural challenges with suggested approaches:}

- **{term/passage}**: {challenge type} → {suggested approach}

## Translation Principles

Rewrite the content into natural, engaging {target_lang} — not merely translate it. Every sentence should read as if a skilled native writer composed it from scratch.

- **Accuracy first**: Facts, data, and logic must match the original exactly
- **Natural flow**: Use idiomatic {target_lang} word order. Break long source sentences into shorter, natural ones. Interpret metaphors and idioms by intended meaning, not word-for-word
- **Terminology**: Use glossary translations consistently. Annotate with original in parentheses on first occurrence of specialized terms
- **Preserve format**: Keep all markdown formatting (headings, bold, italic, images, links, code blocks)
- **Proactive interpretation**: For jargon or concepts the target audience may lack context for, add concise explanations in **bold parentheses** `（**解释**）`. Keep annotations few — only where genuinely needed
```

---

## 第 2 部分：Subagent 启动提示（作为 Agent 工具提示传入）

### 分块模式（每个分块一个 subagent，全部并行启动）

```
Read the translation instructions from: {output_dir}/02-prompt.md

You are translating chunk {NN} of {total_chunks}.
Context: {brief description of what this chunk covers and where it sits in the overall argument}

Translate this chunk:
1. Read `{output_dir}/chunks/chunk-{NN}.md`
2. Translate following the instructions in 02-prompt.md
3. Save translation to `{output_dir}/chunks/chunk-{NN}-draft.md`
```

### 非分块模式

```
Read the translation instructions from: {output_dir}/02-prompt.md

Translate the source file and save the result:
1. Read `{source_file_path}`
2. Save translation to `{output_path}`
```
